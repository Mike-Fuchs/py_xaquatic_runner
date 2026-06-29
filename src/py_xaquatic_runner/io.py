import math
import pandas as pd
from pydantic import ValidationError
from pathlib import Path
import inspect
from . import dataclasses
import xml.etree.ElementTree as ET

AVAILABLE_VERSIONS = {
    obj.model_fields["schema_version"].default: obj
    for name, obj in vars(dataclasses).items()
    if inspect.isclass(obj) and name.startswith("XRunClass_")
}

def xrun_reader(path: str, version: str | None = None):
    raw = parse_xrun_to_dict(path)

    # Decide version: user input > detection
    if version is None:
        version = detect_xrun_version(raw)

    cls = AVAILABLE_VERSIONS.get(version)
    if cls is None:
        raise ValueError(f"Unsupported .xrun version: {version}")

    try:
        # Build the dataclass model (xml_namespace is hardcoded in dataclass)
        obj = cls(**raw)
        return obj

    except ValidationError as e:
        print("❌ Validation failed while building XRunClass:")
        for err in e.errors():
            loc = " → ".join(str(x) for x in err["loc"])
            msg = err["msg"]
            val = err.get("input")
            print(f"  - {loc}: {msg} (got {val})")
        raise

def xrun_writer(obj, path: str):
    """Write an .xrun object back to XML with namespaces and field comments."""
    # Attach namespaces and comments based on model structure
    root = model_to_xml("Parameters", obj)

    nsmap = getattr(obj, "xml_namespace", {})
    for k, v in nsmap.items():
        if v:
            root.set(k, v)

    indent(root)

    with open(path, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
        ET.ElementTree(root).write(f, encoding="utf-8")

def xrun_to_flat_dict(obj) -> dict:
    """Convert a nested XRun dataclass object into a flat dict with dotted keys.
    
    Preserves schema_version as metadata with underscore prefix.
    Converts NaN values to None for JSON compatibility.
    xml_namespace is hardcoded in the dataclass and not exported.
    """
    flat = {}

    def recurse(prefix: str, value):
        if hasattr(value, "model_fields"):  # Pydantic model
            for name, field in value.model_fields.items():
                if name in ("schema_version", "xml_namespace"):
                    continue
                recurse(f"{prefix}.{name}" if prefix else name, getattr(value, name))
        else:
            # Convert NaN to None for JSON compatibility
            if isinstance(value, float) and math.isnan(value):
                flat[prefix] = None
            else:
                flat[prefix] = value

    recurse("", obj)
    
    # Add schema_version as metadata
    flat["_schema_version"] = obj.schema_version
    
    return flat


def flat_dict_to_xrun(flat_dict: dict, version: str | None = None):
    """Convert a flat dict with dotted keys back to XRun dataclass object.
    
    Parameters
    ----------
    flat_dict : dict
        Flat dictionary with dotted keys (from xrun_to_flat_dict or JSON).
    version : str | None
        Schema version to use. If None, reads from "_schema_version" key.
    
    Returns
    -------
    XRunClass
        Reconstructed XRun object with proper validation.
    
    Notes
    -----
    - Converts None to math.nan for float fields
    - Reconstructs nested dict structure from dotted keys
    - xml_namespace is hardcoded in dataclass (not read from dict)
    """
    # Extract metadata
    flat_dict = flat_dict.copy()  # Don't modify original
    version = version or flat_dict.pop("_schema_version", None)
    
    if not version:
        raise ValueError("Schema version not specified and not found in flat_dict['_schema_version']")
    
    # Get the appropriate dataclass
    cls = AVAILABLE_VERSIONS.get(version)
    if cls is None:
        raise ValueError(f"Unsupported .xrun version: {version}")
    
    # Rebuild nested structure from dotted keys
    nested = {}
    for dotted_key, value in flat_dict.items():
        # Skip metadata fields
        if dotted_key.startswith("_"):
            continue
            
        # Convert None back to NaN for float fields
        if value is None:
            value = math.nan
            
        # Split dotted key and build nested dict
        parts = dotted_key.split(".")
        current = nested
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    
    # Instantiate dataclass (Pydantic will validate)
    obj = cls(**nested)
    return obj


def xcp_reader(path: str):
    """
    Parses an xCP configuration XML file and its referenced include files to extract application data.
    Args:
        path (str): Path to the main xCP config XML file.
    Returns:
        pd.DataFrame: A DataFrame containing application details for each field, including:
            - field_id: Identifier of the target field.
            - application_date: Date of application.
            - product_name: Name(s) of the product(s) applied.
            - application_rate: Rate of application.
            - in_crop_buffer: In-crop buffer value.
            - in_field_margin: In-field margin value.
            - minimum_applied_area: Minimum area applied.
            - infection_rate: Infection rate value.
            - micro_macro_ratio: Micro/macro ratio value.
            - smoothing_radius_micro: Smoothing radius for micro.
            - smoothing_radius_macro: Smoothing radius for macro.
            - edge_bias: Edge bias value.
            - edge_width: Edge width value.
            - smoothing_flag: Smoothing flag value.
            - technology_name: Name of the technology used.
            - drift_reduction: Drift reduction value (merged from Technologies include file).
    Notes:
        - The function reads referenced PPMCalendar include files to extract application sequences and parameters.
        - The Technologies include file is parsed to obtain drift reduction values, which are merged into the main DataFrame.
        - All XML files are expected to use the same namespace as the main xCP config file.
    """
    file_dir = Path(path).parent
    tree = ET.parse(path)
    root = tree.getroot()

    # Namespace handling
    ns = root.tag.split('}')[0].strip('{')

    # Find PPMCalendars and collect all PPMCalendar includes
    ppmcal_files = []
    ppmcal_elem = root.find(f'{{{ns}}}PPMCalendars')
    if ppmcal_elem is not None:
        for cal in ppmcal_elem.findall(f'{{{ns}}}PPMCalendar'):
            inc = cal.attrib.get('include')
            if inc:
                ppmcal_files.append(inc)

    # Find Technologies include
    tech_file = None
    tech_elem = root.find(f'{{{ns}}}Technologies')
    if tech_elem is not None:
        tech_file = tech_elem.attrib.get('include')

    # application data frame
    df = pd.DataFrame(columns=["field_id", "application_date", "product_name", "application_rate", "in_crop_buffer", "in_field_margin", "minimum_applied_area", "infection_rate", "micro_macro_ratio",
                               "smoothing_radius_micro", "smoothing_radius_macro", "edge_bias", "edge_width", "smoothing_flag", "technology_name", "drift_reduction"])
    df_rows = []
    
    for ppmcal in ppmcal_files:
        ppm_path = file_dir / ppmcal
        ppm_tree = ET.parse(ppm_path)
        ppm_root = ppm_tree.getroot()
        # Get TargetFields (can be a list of ints)
        target_fields_elem = ppm_root.find(f'{{{ns}}}TargetFields')
        if target_fields_elem is not None:
            target_fields = [int(x) for x in target_fields_elem.text.split(",") if x.strip()]
        else:
            target_fields = []

        # Find all Application elements under ApplicationSequence(s)
        for indication in ppm_root.findall(f'{{{ns}}}Indications'):
            for ind in indication.findall(f'.//{{{ns}}}Indication'):
                for app_seq in ind.findall(f'.//{{{ns}}}ApplicationSequence'):
                    for app in app_seq.findall(f'{{{ns}}}Application'):
                        # Extract parameters from Application
                        tank = app.find(f'{{{ns}}}Tank')
                        products = tank.find(f'{{{ns}}}Products').text if tank is not None and tank.find(f'{{{ns}}}Products') is not None else None
                        app_rate_elem = tank.find(f'.//{{{ns}}}ApplicationRate') if tank is not None else None
                        application_rate = app_rate_elem.text if app_rate_elem is not None else None
                        application_date = app.find(f'{{{ns}}}ApplicationWindow').text if app.find(f'{{{ns}}}ApplicationWindow') is not None else None
                        technology_name = app.find(f'{{{ns}}}Technology').text if app.find(f'{{{ns}}}Technology') is not None else None
                        in_crop_buffer = app.find(f'{{{ns}}}InCropBuffer').text if app.find(f'{{{ns}}}InCropBuffer') is not None else None
                        in_field_margin = app.find(f'{{{ns}}}InFieldMargin').text if app.find(f'{{{ns}}}InFieldMargin') is not None else None
                        minimum_applied_area = app.find(f'{{{ns}}}MinimumAppliedArea').text if app.find(f'{{{ns}}}MinimumAppliedArea') is not None else None
                        infection_rate = app.find(f'{{{ns}}}InfectionRate').text if app.find(f'{{{ns}}}InfectionRate') is not None else None
                        micro_macro_ratio = app.find(f'{{{ns}}}MicroMacroRatio').text if app.find(f'{{{ns}}}MicroMacroRatio') is not None else None
                        smoothing_radius_micro = app.find(f'{{{ns}}}SmoothingRadiusMicro').text if app.find(f'{{{ns}}}SmoothingRadiusMicro') is not None else None
                        smoothing_radius_macro = app.find(f'{{{ns}}}SmoothingRadiusMacro').text if app.find(f'{{{ns}}}SmoothingRadiusMacro') is not None else None
                        edge_bias = app.find(f'{{{ns}}}EdgeBias').text if app.find(f'{{{ns}}}EdgeBias') is not None else None
                        edge_width = app.find(f'{{{ns}}}EdgeWidth').text if app.find(f'{{{ns}}}EdgeWidth') is not None else None
                        smoothing_flag = app.find(f'{{{ns}}}SmoothingFlag').text if app.find(f'{{{ns}}}SmoothingFlag') is not None else None
                        # For each field, create a row
                        for field_id in target_fields:
                            df_rows.append({
                                "field_id": field_id,
                                "application_date": application_date,
                                "product_name": products,
                                "application_rate": application_rate,
                                "in_crop_buffer": in_crop_buffer,
                                "in_field_margin": in_field_margin,
                                "minimum_applied_area": minimum_applied_area,
                                "infection_rate": infection_rate,
                                "micro_macro_ratio": micro_macro_ratio,
                                "smoothing_radius_micro": smoothing_radius_micro,
                                "smoothing_radius_macro": smoothing_radius_macro,
                                "edge_bias": edge_bias,
                                "edge_width": edge_width,
                                "smoothing_flag": smoothing_flag,
                                "technology_name": technology_name,
                                "drift_reduction": None  # to be joined later
                            })
    
    df = pd.DataFrame(df_rows, columns=df.columns)
    
    # Read technologies file to get drift reduction values and merge with df
    tech_df = pd.DataFrame(columns=["technology_name", "drift_reduction"])
    if tech_file:
        tech_path = file_dir / tech_file
        tech_tree = ET.parse(tech_path)
        tech_root = tech_tree.getroot()
        for tech in tech_root.findall(f'{{{ns}}}Technology'):
            tech_name_elem = tech.find(f'{{{ns}}}TechnologyName')
            drift_reduction_elem = tech.find(f'{{{ns}}}DriftReduction')
            tech_name = tech_name_elem.text if tech_name_elem is not None else None
            drift_reduction = drift_reduction_elem.text if drift_reduction_elem is not None else None
            tech_df = pd.concat([
                tech_df,
                pd.DataFrame({
                    "technology_name": [tech_name],
                    "drift_reduction": [drift_reduction]
                })
            ], ignore_index=True)

    # Merge drift_reduction into main df
    if not tech_df.empty:
        df = df.merge(tech_df, on="technology_name", how="left", suffixes=("", "_tech"))
        # Overwrite drift_reduction column with merged value
        df["drift_reduction"] = df["drift_reduction_tech"].combine_first(df["drift_reduction"])
        df = df.drop(columns=["drift_reduction_tech"])

    return df


def xcp_writer(path: str, data: pd.DataFrame) -> Path:
    """
    Writes xCropProtection XML files from application data.
    
    Args:
        path: Path to the output xCropProtection_config.xml file
        data: DataFrame with columns:
            - field_id: int
            - application_date: str (YYYY-MM-DD)
            - product_name: str
            - application_rate: float (g/ha)
            - in_crop_buffer: float (m)
            - in_field_margin: float (m)
            - minimum_applied_area: float (m²)
            - infection_rate: float (0-1)
            - micro_macro_ratio: float (0-1)
            - smoothing_radius_micro: int (odd)
            - smoothing_radius_macro: int (odd)
            - edge_bias: float
            - edge_width: float (m)
            - smoothing_flag: int (1 or 2)
            - technology_name: str
            - drift_reduction: float (0-1)
    
    Creates:
        - xCropProtection_config.xml (main config)
        - Technologies.xml (technology definitions)
        - PPM_Calendar_{field_id}.xml (one per unique field_id)
    """
    output_dir = Path(path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Create Technologies.xml
    technologies = {}
    for _, row in data.iterrows():
        tech_name = row['technology_name']
        if tech_name not in technologies:
            technologies[tech_name] = row['drift_reduction']
    
    tech_list = [
        dataclasses.XCPTechnology(
            TechnologyName=dataclasses.XCPTechnologyName(value=name),
            DriftReduction=dataclasses.XCPDriftReduction(value=drift_red)
        )
        for name, drift_red in technologies.items()
    ]
    
    tech_xml = dataclasses.XCPTechnologies(Technology=tech_list)
    tech_path = output_dir / "Technologies.xml"
    tech_path.write_bytes(tech_xml.to_xml(pretty_print=True, encoding='utf-8'))
    
    # 2. Create PPM_Calendar_*.xml for each field_id
    ppm_calendar_files = []
    for field_id, group in data.groupby('field_id'):
        # Group by application date to create application sequences
        # For simplicity, assume each unique date is one application in a sequence with probability=1
        applications = []
        
        for _, row in group.iterrows():
            # Create Tank with products and application rate
            products = dataclasses.XCPProducts(value=row['product_name'])
            app_rate = dataclasses.XCPApplicationRate(value=row['application_rate'])
            app_rates = dataclasses.XCPApplicationRates(ApplicationRate=app_rate)
            tank = dataclasses.XCPTank(Products=products, ApplicationRates=app_rates)
            
            # Create Application with nested models for each field
            application = dataclasses.XCPApplication(
                Tank=tank,
                ApplicationWindow=dataclasses.XCPApplicationWindow(value=row['application_date']),
                Technology=dataclasses.XCPApplicationTechnology(value=row['technology_name']),
                InCropBuffer=dataclasses.XCPInCropBuffer(value=row['in_crop_buffer']),
                InFieldMargin=dataclasses.XCPInFieldMargin(value=row['in_field_margin']),
                MinimumAppliedArea=dataclasses.XCPMinimumAppliedArea(value=row['minimum_applied_area']),
                InfectionRate=dataclasses.XCPInfectionRate(value=row['infection_rate']),
                MicroMacroRatio=dataclasses.XCPMicroMacroRatio(value=row['micro_macro_ratio']),
                SmoothingRadiusMicro=dataclasses.XCPSmoothingRadiusMicro(value=int(row['smoothing_radius_micro'])),
                SmoothingRadiusMacro=dataclasses.XCPSmoothingRadiusMacro(value=int(row['smoothing_radius_macro'])),
                EdgeBias=dataclasses.XCPEdgeBias(value=row['edge_bias']),
                EdgeWidth=dataclasses.XCPEdgeWidth(value=row['edge_width']),
                SmoothingFlag=dataclasses.XCPSmoothingFlag(value=int(row['smoothing_flag']))
            )
            applications.append(application)
        
        # Create ApplicationSequence with probability=1
        app_sequence = dataclasses.XCPApplicationSequence(
            probability=1.0,
            Application=applications
        )
        
        # Create Indication
        indication = dataclasses.XCPIndication(
            ApplicationSequence=[app_sequence]
        )
        
        # Create Indications container
        indications = dataclasses.XCPIndications(Indication=[indication])
        
        # Get target fields for this calendar (could be multiple if needed)
        # For now, assume one field per calendar
        target_fields = dataclasses.XCPTargetFields(value=str(field_id))
        
        # Create temporal validity
        temporal_validity = dataclasses.XCPTemporalValidity(value='always')
        
        # Create PPMCalendar
        ppm_calendar = dataclasses.XCPPPMCalendar(
            TemporalValidity=temporal_validity,
            TargetFields=target_fields,
            Indications=indications
        )
        
        # Write to file
        calendar_filename = f"PPM_Calendar_{field_id}.xml"
        ppm_calendar_files.append(calendar_filename)
        calendar_path = output_dir / calendar_filename
        calendar_path.write_bytes(ppm_calendar.to_xml(pretty_print=True, encoding='utf-8'))
    
    # 3. Create xCropProtection_config.xml
    ppm_calendar_refs = [
        dataclasses.XCPPPMCalendarRef(include=filename)
        for filename in ppm_calendar_files
    ]
    ppm_calendars = dataclasses.XCPPPMCalendars(PPMCalendar=ppm_calendar_refs)
    technologies_ref = dataclasses.XCPTechnologiesRef(include="Technologies.xml")
    
    config = dataclasses.XCPConfig(
        PPMCalendars=ppm_calendars,
        Technologies=technologies_ref
    )
    
    output_path = Path(path)
    output_path.write_bytes(config.to_xml(pretty_print=True, encoding='utf-8'))




# ==== helper fucntions ====
def flatten_structure(obj, prefix: str = "") -> set[str]:
    """Flatten nested dicts or Pydantic model classes into dotted field paths."""
    fields = set()

    # --- dict case ---
    if isinstance(obj, dict):
        for key, val in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(val, dict):
                fields |= flatten_structure(val, full_key)
            else:
                fields.add(full_key)
        return fields

    # --- Pydantic model class or instance case ---
    model_cls = None
    if hasattr(obj, "model_fields"):
        model_cls = obj
    elif hasattr(obj, "__fields__") or hasattr(obj, "__pydantic_model__"):
        model_cls = obj

    if model_cls is not None:
        for name, field in model_cls.model_fields.items():
            if name in ("schema_version", "xml_namespace"):
                continue
            full_key = f"{prefix}.{name}" if prefix else name
            # If the field type itself is a BaseModel subclass, go deeper
            ftype = getattr(field, "annotation", None)
            if hasattr(ftype, "model_fields"):
                fields |= flatten_structure(ftype, full_key)
            else:
                fields.add(full_key)
        return fields

    # --- fallback ---
    if prefix:
        fields.add(prefix)
    return fields



def detect_xrun_version(data: dict) -> str:
    """
    Detect the .xrun schema version by exact structural match
    against registered XRunClass_* dataclasses.
    """
    data_fields = flatten_structure(data)

    for ver, cls in AVAILABLE_VERSIONS.items():
        model_fields = flatten_structure(cls)
        if data_fields == model_fields:
            return ver

    # If no exact match, optionally give a detailed diff for debugging
    details = []
    for ver, cls in AVAILABLE_VERSIONS.items():
        model_fields = flatten_structure(cls)
        missing = data_fields - model_fields
        extra = model_fields - data_fields
        details.append(
            f"\n--- version {ver} ---\n"
            f"  missing in model: {sorted(missing)[:5]}{'...' if len(missing)>5 else ''}\n"
            f"  extra in model  : {sorted(extra)[:5]}{'...' if len(extra)>5 else ''}"
        )

    raise ValueError(
        "❌ No exact dataclass match found for .xrun structure."
        + "".join(details)
    )


def parse_xrun_to_dict(path: str) -> dict:
    """Parse .xrun XML file to dict structure.
    
    xml_namespace is ignored since it's hardcoded in the dataclass.
    """
    import xml.etree.ElementTree as ET

    tree = ET.parse(path)
    root = tree.getroot()

    # Convert XML to dict for data sections
    data = {}
    for section in root:
        tag = section.tag.split("}", 1)[-1]
        section_data = {
            (e.tag.split("}", 1)[-1]): (e.text.strip() if e.text else "")
            for e in section
        }
        data[tag] = section_data

    return data

def model_to_xml(tag: str, model_obj, level: int = 0) -> ET.Element:
    """Convert a Pydantic model into XML with multi-line indented comments."""
    elem = ET.Element(tag)
    model_cls = type(model_obj)

    for name, field in model_cls.model_fields.items():
        if name in ("schema_version", "xml_namespace"):
            continue
        value = getattr(model_obj, name)

        # Nested model
        if hasattr(value, "model_fields"):
            elem.append(model_to_xml(name, value, level + 1))
            continue

        # Add description as properly indented comment
        if field.description:
            lines = [ln.strip() for ln in field.description.split("@@") if ln.strip()]

            # indentation relative to current nesting level
            base_indent = "  " * (level + 1)
            inner_indent = base_indent + "  "   # +2 spaces inside comment

            # Build the comment body (no <!-- or -->!)
            comment_text = (
                "\n"  # newline after opening <!--
                + "\n".join(f"{inner_indent}{line}" for line in lines)
                + "\n" + base_indent  # closing --> at same indent as opening
            )

            elem.append(ET.Comment(comment_text))

        # Add actual element
        child = ET.Element(name)
        if value is None:
            child.text = ""
        elif isinstance(value, bool):
            child.text = "true" if value else "false"
        elif isinstance(value, float) and math.isnan(value):
            child.text = "NaN"
        else:
            child.text = str(value)
        elem.append(child)

    return elem


def indent(elem: ET.Element, level: int = 0) -> None:
    """Pretty-print XML by adding indentation in-place."""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


    
