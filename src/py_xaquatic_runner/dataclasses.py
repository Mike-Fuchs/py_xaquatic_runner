from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_xml import BaseXmlModel, element, attr
from typing import Literal, Annotated, List

# ==== BaseXAquatic ====
class BaseXAquatic(BaseModel):
    model_config = {"validate_assignment": True}
    
    def copy(self):
        """Return a deep copy of this model."""
        return self.model_copy(deep=True)

# ==== SimulationInfo ====
class SimulationInfo_13(BaseXAquatic):
    SimID: str = Field(...)
    Project: str = Field(...)
    SimulationStart: str = Field(...)
    SimulationEnd: str = Field(...)

# ==== PppUse (includes PatchApp) ====
class PppUse_15(BaseXAquatic):
    ApplicationModule: str = Field(..., description="Parameter     :  ApplicationModule@@Description   :  Specifies the module used for application.@@Values        :  PPM or xCropProtection@@Remark        :  Determines which application module is used for all applications within application sequences.")
    ApplicationRate: Annotated[float, Field(gt=0, description="Parameter     :  ApplicationRate@@Description   :  The application rate in g/ha@@Values        :  Any positive number (or zero)@@Remark        :  The application rate applies to all applications within application sequences.")]
    ApplicationTimeWindow: str = Field(..., description="Parameter     :  ApplicationTimeWindow@@Description   :  The time windows within which applications take place@@Values        :  format: MM-DD to MM-DD[, MM-DD to MM-DD[, ...]]@@Remark        :  For each target field, year and application within an application sequence, a random date within the specified time window is selected. Example values: 04-15 to 04-15 : All fields are applied on 15th of April every year; 04-07 to 04-21 : Every field is applied each year on a random date between 7th and 21st of April; 04-07 to 04-21, 05-02 to 05-16 : Each field is applied twice each year; on a random date between 7th and 21st of April and on a random date between 2nd and 16th of May. 09-23 to 09-23")
    xCropProtectionFilePath: str = Field(..., description="Parameter     :  xCropProtectionFilePath@@Description   :  File name of the xCropProtection configuration file.@@Values        :  File name of the xCropProtection XML file.@@Remark        :  Only the file name is specified here; the path is constructed elsewhere.")
    ProductDatabase: str = Field(..., description="Parameter     :  ProductDatabase@@Description   :  Path to the database file containing product-specific information.@@Values        :  Path to the product database .db, .sqlite, .sqlite3 file.@@Remark        :  Used to specify product data used by xCropProtection.")

class PppUse_14(BaseXAquatic):
    ApplicationRate: Annotated[float, Field(gt=0, description="Parameter     :  ApplicationRate@@Description   :  The application rate in g/ha@@Values        :  Any positive number (or zero)@@Remark        :  The application rate applies to all applications within application sequences.")]
    ApplicationTimeWindow: str = Field(...,description="Parameter     :  ApplicationTimeWindow@@Description   :  The time windows within which applications take place@@Values        :  format: MM-DD to MM-DD[, MM-DD to MM-DD[, ...]]@@Remark        :  For each target field, year and application within an application sequence, a random date within@@                 the specified time window is selected. Example values:@@                 04-15 to 04-15 : All fields are applied on 15th of April every year@@                 04-07 to 04-21 : Every field is applied each year on a random date between 7th and 21st of April@@                 04-07 to 04-21, 05-02 to 05-16 : Each field is applied twice each year; on a random date between@@                                                  7th and 21st of April and on a random date  between 2nd and 16th@@                                                  of May.  09-23 to 09-23")
    
class PppUse_13(BaseXAquatic):
    ApplicationRate: Annotated[float, Field(gt=0, description="Parameter     :  ApplicationRate@@Description   :  The application rate in g/ha@@Values        :  Any positive number (or zero)@@Remark        :  The application rate applies to all applications within application sequences.")]
    ApplicationTimeWindow: str = Field(...,description="Parameter     :  ApplicationTimeWindow@@Description   :  The time windows within which applications take place@@Values        :  format: MM-DD to MM-DD[, MM-DD to MM-DD[, ...]]@@Remark        :  For each target field, year and application within an application sequence, a random date within@@                 the specified time window is selected. Example values:@@                 04-15 to 04-15 : All fields are applied on 15th of April every year@@                 04-07 to 04-21 : Every field is applied each year on a random date between 7th and 21st of April@@                 04-07 to 04-21, 05-02 to 05-16 : Each field is applied twice each year; on a random date between@@                                                  7th and 21st of April and on a random date  between 2nd and 16th@@                                                  of May.  09-23 to 09-23")
    sol_concentration: Annotated[float, Field(ge=0, description="Only DadDrift")]
    AI_density: Annotated[float, Field(gt=0)]
    
# ==== Mitigation ====
class Mitigation_13(BaseXAquatic):
    InCropBuffer: Annotated[float, Field(ge=0, description="Parameter     :  InCropBuffer@@Description   :  A in-crop buffer not applied in meters@@Values        :  Zero or a positive number.@@Remark        :  The in-crop buffer is geometrically applied to the field and might result in very small fields not@@being applied at all.")]
    TechnologyDriftReduction: Annotated[float, Field(ge=0, le=1, description="Parameter     :  TechnologyDriftReduction@@Description   :  The effect of drift-reducing nozzles to spay-drift deposition; the fraction filtered out@@Values        :  A number between 0 and 1@@Remark        :  Zero means no effect = full spray-drift deposition, 1 means full filtering = no deposition at all")]
    InFieldMargin: Annotated[float, Field(ge=0, description="Parameter     :  InFieldMargin@@Description   :  The in-field margin for all fields in the landscape over the entire simulation.@@Values        :  Zero or a positive number.@@Remark        :  Maybe parameterizable at finer scales in future versions.")]
    PatchApplication: bool = Field(..., description="Parameter     :  PatchApp@@Description   :  Controls whether patch application should occur@@Values        :  true or false")
    InfectionRate: Annotated[float, Field(ge=0, le=1, description="Parameter     :  PatchApp@@Description   :  Controls the infection rate (IR) on the fields@@Values        :  0 to 1")]
    MicroMacroRatio: Annotated[float, Field(ge=0, le=1, description="Parameter     :  MicroMacroRatio@@Description   :  Controls the micro/macro ratio in spray drift@@Values        :  0 to 1")]
    SmoothingRadiusMicro: Annotated[int, Field(ge=1, description="Parameter     :  SmoothingRadiusMicro@@Description   :  The smoothing radius for micro deposition maps@@Values        :  Integer ≥ 1")]
    SmoothingRadiusMacro: Annotated[int, Field(ge=1, description="Parameter     :  SmoothingRadiusMacro@@Description   :  The smoothing radius for macro deposition maps@@Values        :  Integer ≥ 1")]
    EdgeBias: Annotated[float, Field(gt=0, description="Parameter     :  EdgeBias@@Description   :  The bias factor for edge smoothing@@Values        :  Floating point number")]
    EdgeWidth: Annotated[float, Field(gt=0, description="Parameter     :  EdgeWidth@@Description   :  The edge width used for mitigation in meters@@Values        :  Floating point number")]
    SmoothingFlag: Annotated[int, Field(ge=1, le=2, description="Parameter     :  SmoothingFlag@@Description   :  Selects macro smoothing mode@@                 1 = focal smoothing@@                 2 = Gaussian seed-based smoothing")]
    
    @field_validator("SmoothingRadiusMicro", "SmoothingRadiusMacro")
    @classmethod
    def must_be_odd(cls, v):
        if v % 2 == 0:
            raise ValueError("Value must be an odd integer ≥ 1")
        return v

# ==== OffField ====
class OffField_16(BaseXAquatic):
    OffFieldRunoffFactor: Annotated[float, Field(ge=0, le=1, description="Parameter     :  OffFieldRunoffFactor@@Description   :  Reduction factor for runoff from field edge to water body due to landscape characteristics@@Values        :  0 to 1 (0 = no reduction, 1 = full reduction)")]
    OffFieldErosionFactor: Annotated[float, Field(ge=0, le=1, description="Parameter     :  OffFieldErosionFactor@@Description   :  Reduction factor for erosion from field edge to water body due to landscape characteristics@@Values        :  0 to 1 (0 = no reduction, 1 = full reduction)")]
    MaximumFieldRunoffArea: Annotated[float, Field(gt=0, description="Parameter     :  MaximumFieldRunoffArea@@Description   :  Maximum area per field that can contribute to runoff and erosion in a reach@@Values        :  Positive number in m²")]

# ==== Compound ====
class Compound_14(BaseXAquatic):
    Substance: str = Field(..., description="Parameter     :  Substance@@Description   :  Used to name the substance that is applied during all applications.@@Values        :  Any text.@@Remark        :  The name itself is mostly a meta-datum but also used to distinguish different substances if@@                     multi-substance experiments are implemented in a future version.")
    MolarMass: Annotated[float, Field(gt=0, description="Parameter     :  MolarMass@@Description   :  The molar mass of the applied substance@@Values        :  A value in g/mol")]
    SaturatedVapourPressure: Annotated[float, Field(gt=0, description="Parameter     :  SaturatedVapourPressure@@Description   :  The saturated vapour pressure of the applied substance at 20°C@@Values        :  A value in Pa")]
    SolubilityInWater: Annotated[float, Field(gt=0, description="Parameter     :  SolubilityInWater@@Description   :  The solubility in water of the applied substance at 20 °C@@Values        :  A concentration (mg/l).")]
    DT50soil: Annotated[float, Field(gt=0, description="Parameter     :  DT50soil@@Description   :  Degradation of active substance in soil@@Values        :  float")]
    Substance_ReferenceMoistureForDT50Soil: Annotated[float, Field(gt=0, description="Parameter     :  Substance_ReferenceMoistureForDT50Soil@@Description   :  The reference moisture for DT50 in soil@@Values        :  A value in %")]
    DT50sw: Annotated[float, Field(gt=0, description="Parameter     :  DT50sw@@Description   :  The half-life transformation time in water of the applied substance at 20 °C@@Values        :  A value in d")]
    DT50sed: Annotated[float, Field(gt=0, description="Parameter     :  DT50sed@@Description   :  The half-life transformation time in sediment of the applied substance at 20 °C@@Values        :  A value in d")]
    KOC: Annotated[float, Field(gt=0, description="Parameter     :  KOC@@Description   :  The organic carbon-water partition coefficient of the applied substance@@Values        :  A value in l/kg@@Remark        :  The KOM used by some modules is automatically derived from the KOC by dividing it by 1.742 <KOC>11.6</KOC>")]
    sol_concentration: Annotated[float, Field(gt=0, description="Parameter     :  spray solution concentration@@Description   :  The concentration of the water-compound spray solution@@Values        :  A value in kg/m³")]
    AI_density: Annotated[float, Field(gt=0, description="Parameter     :  AI density@@Description   :  The density of the active ingredient@@Values        :  A value in kg/m³")]
    FreundlichExponent: Annotated[float, Field(gt=0, description="Parameter     :  FreundlichExponent@@Description   :  The Freundlich exponent in sediment and suspended particles of the applied substance@@Values        :  A value without unit")]
    Substance_PlantUptakeFactor: float = Field(...)
    Substance_PesticideDissipationRateOfFoliage: float = Field(...)
    Substance_FoliarWashOffCoefficient: float = Field(...)
    Substance_HenryConstant: float = Field(...)
    Substance_TemperatureAtWhichMeasured: float = Field(...)

class Compound_13(BaseXAquatic):
    Substance: str = Field(..., description="Parameter     :  Substance@@Description   :  Used to name the substance that is applied during all applications.@@Values        :  Any text.@@Remark        :  The name itself is mostly a meta-datum but also used to distinguish different substances if@@                     multi-substance experiments are implemented in a future version.")
    MolarMass: Annotated[float, Field(gt=0, description="Parameter     :  MolarMass@@Description   :  The molar mass of the applied substance@@Values        :  A value in g/mol")]
    SaturatedVapourPressure: Annotated[float, Field(gt=0, description="Parameter     :  SaturatedVapourPressure@@Description   :  The saturated vapour pressure of the applied substance at 20°C@@Values        :  A value in Pa")]
    SolubilityInWater: Annotated[float, Field(gt=0, description="Parameter     :  SolubilityInWater@@Description   :  The solubility in water of the applied substance at 20 °C@@Values        :  A concentration (mg/l).")]
    DT50soil: Annotated[float, Field(gt=0, description="Parameter     :  DT50soil@@Description   :  Degradation of active substance in soil@@Values        :  float")]
    Substance_ReferenceMoistureForDT50Soil: Annotated[float, Field(gt=0)]
    DT50sw: Annotated[float, Field(gt=0, description="Parameter     :  DT50sw@@Description   :  The half-life transformation time in water of the applied substance at 20 °C@@Values        :  A value in d")]
    DT50sed: Annotated[float, Field(gt=0, description="Parameter     :  DT50sed@@Description   :  The half-life transformation time in sediment of the applied substance at 20 °C@@Values        :  A value in d")]
    KOC: Annotated[float, Field(gt=0, description="Parameter     :  KOC@@Description   :  The organic carbon-water partition coefficient of the applied substance@@Values        :  A value in l/kg@@Remark        :  The KOM used by some modules is automatically derived from the KOC by dividing it by 1.742 <KOC>11.6</KOC>")]
    sol_concentration: Annotated[float, Field(gt=0)]
    FreundlichExponent: Annotated[float, Field(gt=0, description="Parameter     :  FreundlichExponent@@Description   :  The Freundlich exponent in sediment and suspended particles of the applied substance@@Values        :  A value without unit")]
    Substance_PlantUptakeFactor: float = Field(...)
    Substance_PesticideDissipationRateOfFoliage: float = Field(...)
    Substance_FoliarWashOffCoefficient: float = Field(...)
    Substance_HenryConstant: float = Field(...)
    Substance_TemperatureAtWhichMeasured: float = Field(...)

# ==== Exposure ====
class Exposure_13(BaseXAquatic):
    SimulateSprayDriftExposure: bool = Field(..., description="Parameter     :  SimulateSprayDriftExposure@@Description   :  Controls whether spray-drift exposure is simulated or not.@@Values        :  \"true\" or \"false.@@Remark        :  At least one of SimulateRunOffExposure and SimulateSprayDriftExposure should be true.")
    RunDadDrift: bool = Field(..., description="Parameter     :  RunDadDrift@@Description   :  Controles if submodel is run@@Values        :  \"true\" or \"false.")
    RunXSprayDrift: bool = Field(..., description="Parameter     :  RunXSprayDrift@@Description   :  Controles if submodel is run@@Values        :  \"true\" or \"false.")
    SimulateRunOffExposure: bool = Field(...,description="Parameter     :  RunStepsRiverNetwork@@Description   :  Controls whether environmental fate is calculated by the StepsRiverNetwork component@@Values        :  true or false")
    SimulateDrainageExposure: bool = Field(...,description="Parameter     :  FocusMacro@@Description   :  Controls whether soil efate is calculated by the FocusMacro component@@Values        :  true or false")
    CropStage: str = Field(..., description="Parameter     :  XDrift@@Description   :  Controls the crop stage@@Values        :  arable or early")
    DepositionInputFile: str = Field(...)
    FocusMacro_ZFINT: float = Field(...)
    SprayApplication_PrzmApplicationMethod: str = Field(...)
    SprayApplication_IncorporationDepth: float = Field(...)
    FocusPrzm_Crop: str = Field(..., description="Parameter     :  FocusPrzm@@Description   :  Controls the crop@@Values        :  Cereals,Winter|OffCrop|Oilseedrape,Winter")
    WindDirection: float = Field(...,description="WindDirection: Wind 270 means that the wind is coming from the west, and blowing towards the east.@@| Direction Name | Abbreviation | Cardinal Degrees |@@| North          | N            | 0°      |@@| North-Northeast| NNE          | 22.5°   |@@| Northeast      | NE           | 45°     |@@| East-Northeast | ENE          | 67.5°   |@@| East           | E            | 90°     |@@| East-Southeast | ESE          | 112.5°  |@@| Southeast      | SE           | 135°    |@@| South-Southeast| SSE          | 157.5°  |@@| South          | S            | 180°    |@@| South-Southwest| SSW          | 202.5°  |@@| Southwest      | SW           | 225°    |@@| West-Southwest | WSW          | 247.5°  |@@| West           | W            | 270°    |@@| West-Northwest | WNW          | 292.5°  |@@| Northwest      | NW           | 315°    |@@| North-Northwest| NNW          | 337.5°  |")
    DynamicReachShapes: bool = Field(...)
    roughness_height: float = Field(...)
    canopy_height: float = Field(...)
    LAI: float = Field(...)
    boom_height: float = Field(...)
    boom_width: float = Field(...)
    DSD: str = Field(...)
    nozzle_angle: float = Field(...)
    app_pres: float = Field(...)
    max_dist: float = Field(...)
    dep_height: float = Field(...)
    n_threads: int = Field(..., description="Parameter     :  DadDrift@@Description   :  Controls the number of logical cores available to the components@@Values        :  integer 1 upwards")
    
    @field_validator("CropStage")
    @classmethod
    def validate_crop_stage(cls, v):
        allowed = {"early", "late", "arable"}
        if v.lower() not in allowed:
            raise ValueError(f"CropStage must be one of {', '.join(allowed)} (got '{v}')")
        return v.lower()
    
    @field_validator("DepositionInputFile", mode="before")
    @classmethod
    def default_empty_str(cls, v):
        """Allow None or empty string, and normalize None to ''."""
        return v or ""
    
# ==== Fate ====
class Fate_13(BaseXAquatic):
    RunStepsRiverNetwork: bool = Field(...)
    
# ==== Effect ====
class Effect_14(BaseXAquatic):
    RunCvasiLemLandscape: bool = Field(..., description="Parameter     :  RunCvasiLemLandscape(Lemna-SETAC but it Takes the influence of water velocity on growth)@@Description   :  Controls whether the Lemna Landscape model is excuted or not @@Values        :  true or false")
    k_photo_max: float = Field(...,description="Parameter     :  k_photo_max@@Description   :  Maximum photolysis rate constant in the Lemna model@@Values        :  A value in 1/d")
    EC50_int: float = Field(...,description="Parameter     :  EC50@@Description   :  Effective Concentration for 50% of the test population in the Lemna model@@Values        :  A value in µg/L")
    b: float = Field(...,description="Parameter     :  b@@Description   :  Shape-correction or slope parameter  in the Lemna model@@Values        :  A value without unit")
    P: float = Field(...,description="Parameter     :  P@@Description   :  permeability (cm d-1), substance specific@@Values        :  A value in cm/d")

# ==== Effect v1.6 ====
class Effect_16(BaseXAquatic):
    RunCvasiLemLandscape: bool = Field(..., description="Parameter     :  RunCvasiLemLandscape(Lemna-SETAC but it Takes the influence of water velocity on growth)@@Description   :  Controls whether the Lemna Landscape model is excuted or not @@Values        :  true or false")
    k_photo_max: float = Field(...,description="Parameter     :  k_photo_max@@Description   :  Maximum photolysis rate constant in the Lemna model@@Values        :  A value in 1/d")
    EC50_int: float = Field(...,description="Parameter     :  EC50@@Description   :  Effective Concentration for 50% of the test population in the Lemna model@@Values        :  A value in µg/L")
    b: float = Field(...,description="Parameter     :  b@@Description   :  Shape-correction or slope parameter  in the Lemna model@@Values        :  A value without unit")
    P: float = Field(...,description="Parameter     :  P@@Description   :  permeability (cm d-1), substance specific@@Values        :  A value in cm/d")
    window_length: Annotated[int, Field(gt=0, description="Parameter     :  window_length@@Description   :  Length of the moving time window for EPx calculation@@Values        :  A positive integer in days")]
    step_width: Annotated[int, Field(gt=0, description="Parameter     :  step_width@@Description   :  Step size of the moving time window for EPx calculation@@Values        :  A positive integer in days")]
    K_pw: float = Field(..., description="Parameter     :  K_pw@@Description   :  Plant-water partition coefficient in the Lemna model@@Values        :  A value without unit")
    exposure_threshold: float = Field(..., description="Parameter     :  exposure_threshold@@Description   :  Concentration threshold below which exposure values are set to zero before effect simulation. Prevents ODE solver instability from sub-threshold concentration pulses. Intended for future use as EPAT (Exposure Profile Above Threshold) in regulatory modelling.@@Values        :  A value in µg/L")
    exposure_scaling_factor: float = Field(1.0, description="Parameter     :  exposure_scaling_factor@@Description   :  Multiplier applied to the exposure (PEC) time series fed to the effect model at input preparation, scaling the exposure the CvasiLemLandscape component sees. The reported PEC output is unchanged.@@Values        :  A positive number; 1.0 = no scaling (default)")

# ==== Observer ====
class Observer_151(BaseXAquatic):
    NamesTarget: str = Field(..., description="Parameter     :  NamesTarget@@Description   :  Human-readable labels for target reaches used in plots and output file names.@@Values        :  Comma-separated list of strings, e.g. 'Upstream,Outlet,Tributary'@@Remark        :  Must have the same number of entries as KeysTarget.@@                 Leave empty to skip target-reach reporting.")
    KeysTarget: str = Field(...,description="Parameter     :  KeysTarget@@Description   :  Internal reach IDs (key_r) for target reaches, as used in the model and geo data.@@Values        :  Comma-separated list of reach keys, e.g. 'r1,r5,r12'@@Remark        :  Must have the same number of entries as NamesTarget.")

# ==== SimulationInfo v1.7 ====
class SimulationInfo_17(BaseXAquatic):
    SimID: str = Field(...)
    Project: str = Field(...)
    SimulationStart: str = Field(...)
    SimulationEnd: str = Field(...)
    ncores: int = Field(1, description="Parameter     :  ncores@@Description   :  Number of logical cores/threads for module-internal parallelisation (FocusMacro, DadDrift, RunOffPrzm, CvasiLemLandscape).@@Values        :  -1 = all available cores; or a positive integer")
    TargetType: int = Field(115, description="Parameter     :  TargetType@@Description   :  LULCTypeID value that identifies the target (crop) fields the product is applied to by PPM.@@Values        :  A positive integer matching a LULC.shp LULCTypeID code")
    HabitatTypes: str = Field("999", description="Parameter     :  HabitatTypes@@Description   :  LULCTypeID value(s) that identify off-field habitats receiving spray drift (XSprayDrift).@@Values        :  A single integer or a comma+space list, e.g. '999' or '422, 999'")
    FeatureTypeAttribute: str = Field("LULCTypeID", description="Parameter     :  FeatureTypeAttribute@@Description   :  Name of the LULC.shp column exposed by LandscapeScenario as the feature-type code (FeatureTypeIds).@@Values        :  A shapefile column name, e.g. 'LULCTypeID'")
    DeleteProcessingFolder: bool = Field(False, description="Parameter     :  DeleteProcessingFolder@@Description   :  If true, the run's intermediate 'processing' folder is deleted at the end of the run (saves disk space; intermediate per-component files are then unavailable for inspection). If false, the processing folder is kept.@@Values        :  true or false")

# ==== PppUse v1.7 ====
class PppUse_17(BaseXAquatic):
    ApplicationModule: str = Field(..., description="Parameter     :  ApplicationModule@@Description   :  Specifies the module used for application.@@Values        :  PPM or xCropProtection@@Remark        :  Determines which application module is used for all applications within application sequences.")
    ApplicationRate: Annotated[float, Field(gt=0, description="Parameter     :  ApplicationRate@@Description   :  The application rate in g/ha@@Values        :  Any positive number (or zero)@@Remark        :  The application rate applies to all applications within application sequences.")]
    ApplicationTimeWindow: str = Field(..., description="Parameter     :  ApplicationTimeWindow@@Description   :  The time windows within which applications take place@@Values        :  format: MM-DD to MM-DD[, MM-DD to MM-DD[, ...]]@@Remark        :  For each target field, year and application within an application sequence, a random date within the specified time window is selected. Example values: 04-15 to 04-15 : All fields are applied on 15th of April every year; 04-07 to 04-21 : Every field is applied each year on a random date between 7th and 21st of April; 04-07 to 04-21, 05-02 to 05-16 : Each field is applied twice each year; on a random date between 7th and 21st of April and on a random date between 2nd and 16th of May. 09-23 to 09-23")
    UseFocusApplicationTimer: bool = Field(False, description="Parameter     :  UseFocusApplicationTimer@@Description   :  If true, the FocusApplicationTimer derives application dates and ApplicationTimeWindow is ignored.@@Values        :  true or false")
    FocusBBCH: str = Field("12", description="Parameter     :  FocusBBCH@@Description   :  BBCH growth stage the application window is keyed to (crop and FOCUS scenario are per field from LULC.shp).@@Values        :  A BBCH stage 0-99, or n.s. for permanent crops")
    xCropProtectionFilePath: str = Field(..., description="Parameter     :  xCropProtectionFilePath@@Description   :  Path to the xCropProtection configuration file, used by the model as-is (no auto path construction).@@Values        :  A path to the xCropProtection XML relative to the model root (or absolute).@@Remark        :  User-provided application pattern; kept outside the fixed scenario, e.g. under samples/xCropProtection/.")
    ProductDatabase: str = Field("", description="Parameter     :  ProductDatabase@@Description   :  Path to the database file containing product-specific information.@@Values        :  Path to the product database .db, .sqlite, .sqlite3 file, or empty.@@Remark        :  Currently not needed - kept for future use; leave empty. xCropProtection only uses it to convert products declared 'other/products' to active substances; with 'other/active_substances' (the default) each product name is used directly as the active substance (Product = AI).")

# ==== Exposure v1.7 ====
class Exposure_17(BaseXAquatic):
    SimulateSprayDriftExposure: bool = Field(..., description="Parameter     :  SimulateSprayDriftExposure@@Description   :  Controls whether spray-drift exposure is simulated or not.@@Values        :  \"true\" or \"false.@@Remark        :  At least one of SimulateRunOffExposure and SimulateSprayDriftExposure should be true.")
    RunDadDrift: bool = Field(..., description="Parameter     :  RunDadDrift@@Description   :  Controles if submodel is run@@Values        :  \"true\" or \"false.")
    RunXSprayDrift: bool = Field(..., description="Parameter     :  RunXSprayDrift@@Description   :  Controles if submodel is run@@Values        :  \"true\" or \"false.")
    RunFocusDrift: bool = Field(False, description="Parameter     :  RunFocusDrift@@Description   :  Controls whether the FOCUS Step 3 drift engine (FocusDrift) is run. Mutually exclusive with RunDadDrift/RunXSprayDrift.@@Values        :  \"true\" or \"false.")
    SimulateRunOffExposure: bool = Field(...,description="Parameter     :  RunStepsRiverNetwork@@Description   :  Controls whether environmental fate is calculated by the StepsRiverNetwork component@@Values        :  true or false")
    SimulateDrainageExposure: bool = Field(...,description="Parameter     :  FocusMacro@@Description   :  Controls whether soil efate is calculated by the FocusMacro component@@Values        :  true or false")
    CropStage: str = Field(..., description="Parameter     :  XDrift@@Description   :  Controls the crop stage@@Values        :  arable or early")
    DepositionInputFile: str = Field(...)
    FocusMacro_ZFINT: float = Field(...)
    SprayApplication_PrzmApplicationMethod: str = Field(...)
    SprayApplication_IncorporationDepth: float = Field(...)
    PRZM_AMC: str = Field("AMC-II", description="Parameter     :  PRZM_AMC@@Description   :  Antecedent moisture condition the runoff curve-number override runs on.@@Values        :  AMC-I (dry), AMC-II (average) or AMC-III (wet)")
    PRZM_CN_METHOD: str = Field("FOCUS", description="Parameter     :  PRZM_CN_METHOD@@Description   :  Method used to derive the runoff curve number for the override.@@Values        :  FOCUS or TR55")
    PRZM_RunMode: str = Field("windowed", description="Parameter     :  PRZM_RunMode@@Description   :  How RunOffPrzm runs PRZM over time. windowed = one run per application year with 2 warm-up years (engine-safe default); continuous = a single real multi-year run carrying every application.@@Values        :  windowed or continuous")
    WindDirection: float = Field(...,description="WindDirection: Wind 270 means that the wind is coming from the west, and blowing towards the east.@@| Direction Name | Abbreviation | Cardinal Degrees |@@| North          | N            | 0°      |@@| North-Northeast| NNE          | 22.5°   |@@| Northeast      | NE           | 45°     |@@| East-Northeast | ENE          | 67.5°   |@@| East           | E            | 90°     |@@| East-Southeast | ESE          | 112.5°  |@@| Southeast      | SE           | 135°    |@@| South-Southeast| SSE          | 157.5°  |@@| South          | S            | 180°    |@@| South-Southwest| SSW          | 202.5°  |@@| Southwest      | SW           | 225°    |@@| West-Southwest | WSW          | 247.5°  |@@| West           | W            | 270°    |@@| West-Northwest | WNW          | 292.5°  |@@| Northwest      | NW           | 315°    |@@| North-Northwest| NNW          | 337.5°  |")
    DynamicReachShapes: bool = Field(...)
    roughness_height: float = Field(...)
    canopy_height: float = Field(...)
    LAI: float = Field(...)
    boom_height: float = Field(...)
    boom_width: float = Field(...)
    DSD: str = Field(...)
    nozzle_angle: float = Field(...)
    app_pres: float = Field(...)
    max_dist: float = Field(...)
    dep_height: float = Field(...)
    RunoffMethod: str = Field("PRZM", description="Parameter     :  RunoffMethod@@Description   :  Which engine computes surface runoff. PRZM uses RunOffPrzm (runoff + erosion); MACRO uses FocusMacro surface runoff (no erosion).@@Values        :  PRZM or MACRO")
    RunoffFromPrzm: bool = Field(True, description="Parameter     :  RunoffFromPrzm@@Description   :  Derived from RunoffMethod (do not edit) - gates the RunOffPrzm wires into RunOffToReach.@@Values        :  true when RunoffMethod == PRZM")
    RunoffFromMacro: bool = Field(False, description="Parameter     :  RunoffFromMacro@@Description   :  Derived from RunoffMethod (do not edit) - gates the FocusMacro surface-runoff wires into RunOffToReach.@@Values        :  true when RunoffMethod == MACRO")
    FocusDrift_Waterbody: str = Field("STREAM", description="Parameter     :  FocusDrift_Waterbody@@Description   :  FOCUS waterbody type the Step 3 edge-of-field drift is computed for.@@Values        :  STREAM, DITCH or POND")
    FocusDrift_Crop: str = Field("", description="Parameter     :  FocusDrift_Crop@@Description   :  Optional global FOCUS crop code override; when empty the per-field CROP attribute from LULC.shp is used.@@Values        :  A FOCUS crop code (e.g. WCEREALS, MAIZE, POMEL) or empty")
    FocusDrift_Method: str = Field("repair", description="Parameter     :  FocusDrift_Method@@Description   :  FOCUS multi-application rule. repair = each application uses the (n-i+1)-app coefficients; classic = every application uses the n-app coefficients.@@Values        :  repair or classic")
    FocusDrift_DriftReduction: float = Field(0.0, description="Parameter     :  FocusDrift_DriftReduction@@Description   :  Drift reduction percentage (DRN) applied to the FOCUS deposition.@@Values        :  A number between 0 and 100")
    FocusDrift_NoSprayZone: float = Field(0.0, description="Parameter     :  FocusDrift_NoSprayZone@@Description   :  No-spray zone width (NSZ) added to the crop buffer before computing drift.@@Values        :  Zero or a positive number in metres")

    @field_validator("CropStage")
    @classmethod
    def validate_crop_stage(cls, v):
        allowed = {"early", "late", "arable"}
        if v.lower() not in allowed:
            raise ValueError(f"CropStage must be one of {', '.join(allowed)} (got '{v}')")
        return v.lower()

    @field_validator("DepositionInputFile", mode="before")
    @classmethod
    def default_empty_str(cls, v):
        """Allow None or empty string, and normalize None to ''."""
        return v or ""

    @field_validator("PRZM_AMC")
    @classmethod
    def validate_przm_amc(cls, v):
        allowed = {"AMC-I", "AMC-II", "AMC-III"}
        canonical = str(v).upper()
        if canonical not in allowed:
            raise ValueError(f"PRZM_AMC must be one of {', '.join(sorted(allowed))} (got '{v}')")
        return canonical

    @field_validator("PRZM_CN_METHOD")
    @classmethod
    def validate_przm_cn_method(cls, v):
        allowed = {"FOCUS", "TR55"}
        canonical = str(v).upper()
        if canonical not in allowed:
            raise ValueError(f"PRZM_CN_METHOD must be one of {', '.join(sorted(allowed))} (got '{v}')")
        return canonical

    @field_validator("PRZM_RunMode")
    @classmethod
    def validate_przm_run_mode(cls, v):
        allowed = {"windowed", "continuous"}
        canonical = str(v).lower()
        if canonical not in allowed:
            raise ValueError(f"PRZM_RunMode must be one of {', '.join(sorted(allowed))} (got '{v}')")
        return canonical

    @field_validator("RunoffMethod")
    @classmethod
    def validate_runoff_method(cls, v):
        allowed = {"PRZM", "MACRO"}
        canonical = str(v).upper()
        if canonical not in allowed:
            raise ValueError(f"RunoffMethod must be one of {', '.join(sorted(allowed))} (got '{v}')")
        return canonical

    @field_validator("FocusDrift_Waterbody")
    @classmethod
    def validate_focus_drift_waterbody(cls, v):
        allowed = {"STREAM", "DITCH", "POND"}
        if str(v).strip().upper() not in allowed:
            raise ValueError(f"FocusDrift_Waterbody must be one of {', '.join(sorted(allowed))} (got '{v}')")
        return str(v).strip().upper()

    @field_validator("FocusDrift_Method")
    @classmethod
    def validate_focus_drift_method(cls, v):
        allowed = {"classic", "repair"}
        if str(v).strip().lower() not in allowed:
            raise ValueError(f"FocusDrift_Method must be one of {', '.join(sorted(allowed))} (got '{v}')")
        return str(v).strip().lower()

    @model_validator(mode="before")
    @classmethod
    def derive_runoff_gates(cls, data):
        """RunoffFromPrzm/RunoffFromMacro are derived from RunoffMethod; supplied values are overridden."""
        if isinstance(data, dict):
            method = str(data.get("RunoffMethod", "PRZM")).upper()
            data["RunoffFromPrzm"] = method == "PRZM"
            data["RunoffFromMacro"] = method == "MACRO"
        return data

# ==== Fate v1.7 ====
class Fate_17(BaseXAquatic):
    RunStepsRiverNetwork: bool = Field(...)
    SubstepsPerDay: int = Field(8640, description="Parameter     :  SubstepsPerDay@@Description   :  Number of StepsRiverNetwork integration sub-steps per day. Finer sub-steps stabilise the explicit STEPS scheme on large catchments (the coarse default can produce negative concentrations). Only used when RunStepsRiverNetwork is true.@@Values        :  1440 = 1 min, 8640 = 10 s (default), 86400 = 1 s (must divide 86400 evenly)")
    EfateEngine: str = Field("auto", description="Parameter     :  EfateEngine@@Description   :  Which StepsRiverNetwork efate engine runs the fate integration. auto = numba if the compiled kernel is available else numpy; numba = compiled (fast, recommended for large catchments); numpy = the reference implementation. Only used when RunStepsRiverNetwork is true.@@Values        :  auto (default), numba or numpy")
    EfateEngineBlockSize: str = Field("", description="Parameter     :  EfateEngineBlockSize@@Description   :  Numba engine only: days of results buffered before each HDF5 write. Empty = whole run in one block (fastest, most memory); N = N days per block. Only used when RunStepsRiverNetwork is true and EfateEngine resolves to numba.@@Values        :  empty (default) or a positive integer number of days")

    @field_validator("SubstepsPerDay")
    @classmethod
    def validate_substeps_per_day(cls, v):
        value = int(v)
        if value <= 0 or 86400 % value != 0:
            raise ValueError(f"SubstepsPerDay must be a positive divisor of 86400 (got '{v}')")
        return value

    @field_validator("EfateEngine")
    @classmethod
    def validate_efate_engine(cls, v):
        allowed = {"auto", "numba", "numpy"}
        canonical = str(v).lower()
        if canonical not in allowed:
            raise ValueError(f"EfateEngine must be one of {', '.join(sorted(allowed))} (got '{v}')")
        return canonical

    @field_validator("EfateEngineBlockSize", mode="before")
    @classmethod
    def validate_efate_engine_block_size(cls, v):
        if v is None:
            return ""
        s = str(v).strip()
        if s == "":
            return ""
        if not s.isdigit() or int(s) <= 0:
            raise ValueError(f"EfateEngineBlockSize must be empty or a positive integer number of days (got '{v}')")
        return s

# ==== Effect v1.7 ====
class Effect_17(BaseXAquatic):
    RunCvasiLemLandscape: bool = Field(..., description="Parameter     :  RunCvasiLemLandscape(Lemna-SETAC but it Takes the influence of water velocity on growth)@@Description   :  Controls whether the Lemna Landscape model is excuted or not @@Values        :  true or false")
    k_photo_max: float = Field(...,description="Parameter     :  k_photo_max@@Description   :  Maximum photolysis rate constant in the Lemna model@@Values        :  A value in 1/d")
    EC50_int: float = Field(...,description="Parameter     :  EC50@@Description   :  Effective Concentration for 50% of the test population in the Lemna model@@Values        :  A value in µg/L")
    b: float = Field(...,description="Parameter     :  b@@Description   :  Shape-correction or slope parameter  in the Lemna model@@Values        :  A value without unit")
    P: float = Field(...,description="Parameter     :  P@@Description   :  permeability (cm d-1), substance specific@@Values        :  A value in cm/d")
    window_length: Annotated[int, Field(gt=0, description="Parameter     :  window_length@@Description   :  Length of the moving time window for EPx calculation@@Values        :  A positive integer in days")]
    step_width: Annotated[int, Field(gt=0, description="Parameter     :  step_width@@Description   :  Step size of the moving time window for EPx calculation@@Values        :  A positive integer in days")]
    K_pw: float = Field(..., description="Parameter     :  K_pw@@Description   :  Plant-water partition coefficient in the Lemna model@@Values        :  A value without unit")
    exposure_threshold: float = Field(..., description="Parameter     :  exposure_threshold@@Description   :  Concentration threshold below which exposure values are set to zero before effect simulation. Prevents ODE solver instability from sub-threshold concentration pulses. Intended for future use as EPAT (Exposure Profile Above Threshold) in regulatory modelling.@@Values        :  A value in µg/L")
    exposure_scaling_factor: Annotated[float, Field(gt=0, description="Parameter     :  exposure_scaling_factor@@Description   :  Multiplier applied to the exposure (PEC) time series fed to the effect model at input preparation, scaling the exposure the CvasiLemLandscape component sees. The reported PEC output is unchanged.@@Values        :  A positive number; 1.0 = no scaling (default)")] = 1.0
    solver: str = Field("bdf", description="Parameter     :  solver@@Description   :  deSolve ODE solver used by the Lemna effect model. bdf (backward differentiation, CVODE-style) is robust on the flickering on/off exposure series; the cvasi default (lsoda) can destabilise.@@Values        :  bdf (recommended), vode, lsode, lsodes, radau, lsoda")
    solver_tolerance: float = Field(1e-6, description="Parameter     :  solver_tolerance@@Description   :  Absolute and relative error tolerance (atol = rtol) for the ODE solver.@@Values        :  A small positive number, e.g. 1e-6")
    lemna_velocity_ms_predefined: float = Field(0.01, description="Parameter     :  lemna_velocity_ms_predefined@@Description   :  Constant water velocity used as the Lemna growth forcing, overriding the flow-derived velocity.@@Values        :  A value in m/s; 0.01 = previous default")
    compute_epx: bool = Field(True, description="Parameter     :  compute_epx@@Description   :  Whether the effect percentiles (EP10/EP50) are computed. Off = faster biomass-only run, EPx set to -99.@@Values        :  true (default) or false")

# ==== XRunClass v1.7 ====
class XRunClass_17(BaseXAquatic):
    schema_version: Literal["1.7"] = "1.7"

    xml_namespace: dict[str, str] = Field(
        default_factory=lambda: {
            "xmlns": "urn:xAquaticRisk",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "urn:xAquaticRisk model/variant/parameters.xsd",
        }
    )

    SimulationInfo: SimulationInfo_17
    PppUse: PppUse_17
    Mitigation: Mitigation_13
    OffField: OffField_16
    Compound: Compound_14
    Exposure: Exposure_17
    Fate: Fate_17
    Effect: Effect_17
    Observer: Observer_151

# ==== XRunClass v1.6 ====
class XRunClass_16(BaseXAquatic):
    schema_version: Literal["1.6"] = "1.6"
    
    xml_namespace: dict[str, str] = Field(
        default_factory=lambda: {
            "xmlns": "urn:xAquaticRisk",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "urn:xAquaticRisk model/variant/parameters.xsd",
        }
    )
    
    SimulationInfo: SimulationInfo_13
    PppUse: PppUse_15
    Mitigation: Mitigation_13
    OffField: OffField_16
    Compound: Compound_14
    Exposure: Exposure_13
    Fate: Fate_13
    Effect: Effect_16
    Observer: Observer_151

# ==== XRunClass v1.5.1 ====
class XRunClass_151(BaseXAquatic):
    schema_version: Literal["1.5.1"] = "1.5.1"
    
    xml_namespace: dict[str, str] = Field(
        default_factory=lambda: {
            "xmlns": "urn:xAquaticRisk",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "urn:xAquaticRisk model/variant/parameters.xsd",
        }
    )
    
    SimulationInfo: SimulationInfo_13
    PppUse: PppUse_15
    Mitigation: Mitigation_13
    Compound: Compound_14
    Exposure: Exposure_13
    Fate: Fate_13
    Effect: Effect_14
    Observer: Observer_151    

# ==== XRunClass v1.5 ====
class XRunClass_15(BaseXAquatic):
    schema_version: Literal["1.5"] = "1.5"
    
    xml_namespace: dict[str, str] = Field(
        default_factory=lambda: {
            "xmlns": "urn:xAquaticRisk",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "urn:xAquaticRisk model/variant/parameters.xsd",
        }
    )
    
    SimulationInfo: SimulationInfo_13
    PppUse: PppUse_15
    Mitigation: Mitigation_13
    Compound: Compound_14
    Exposure: Exposure_13
    Fate: Fate_13
    Effect: Effect_14
    
# ==== XRunClass v1.4 ====
class XRunClass_14(BaseXAquatic):
    schema_version: Literal["1.4"] = "1.4"
    
    xml_namespace: dict[str, str] = Field(
        default_factory=lambda: {
            "xmlns": "urn:xAquaticRisk",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "urn:xAquaticRisk model/variant/parameters.xsd",
        }
    )
    
    SimulationInfo: SimulationInfo_13
    PppUse: PppUse_14
    Mitigation: Mitigation_13
    Compound: Compound_14
    Exposure: Exposure_13
    Fate: Fate_13
    Effect: Effect_14
    
# ==== XRunClass v1.3 ====
class XRunClass_13(BaseXAquatic):
    schema_version: Literal["1.3"] = "1.3"
    
    xml_namespace: dict[str, str] = Field(
        default_factory=lambda: {
            "xmlns": "urn:xAquaticRisk",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "urn:xAquaticRisk model/variant/parameters.xsd",
        }
    )
    
    SimulationInfo: SimulationInfo_13
    PppUse: PppUse_14
    Mitigation: Mitigation_13
    Compound: Compound_13
    Exposure: Exposure_13
    Fate: Fate_13

# ==== Project configuration ====
class XRunConfig(BaseModel):
    python_exe: str = Field(..., description="Relative path to model Python executable (e.g. %CD%/model/core/bin/python.exe)")
    xland_script: str = Field(..., description="Relative path to model init script (e.g. %CD%/model/core/init.py)")
    xland_input: str = Field(..., description="Placeholder; auto-generated by scheduler for each run")
    project_folder: str = Field(..., description="The top level folder where the XAquatic project is stored.")

# ==== XML data structures for xCP writing (using pydantic-xml) ====
# ==== xCropProtection Config XML ====
class XCPPPMCalendarRef(BaseXmlModel, tag='PPMCalendar'):
    """
    Reference to a PPMCalendar XML file.
    XML: <PPMCalendar include="PPM_Calendar_384.xml"/>
    """
    include: str = attr()

class XCPPPMCalendars(BaseXmlModel, tag='PPMCalendars'):
    """
    Container for PPMCalendar references.
    XML:
        <PPMCalendars>
            <PPMCalendar include="PPM_Calendar_384.xml"/>
            <PPMCalendar include="PPM_Calendar_556.xml"/>
        </PPMCalendars>
    """
    PPMCalendar: List[XCPPPMCalendarRef] = element(tag='PPMCalendar', default=[])

class XCPTechnologiesRef(BaseXmlModel, tag='Technologies'):
    """
    Reference to Technologies XML file.
    XML: <Technologies include="Technologies.xml"/>
    """
    include: str = attr()

class XCPConfig(BaseXmlModel, tag='xCropProtection', nsmap={'': 'urn:xCropProtectionLandscapeScenarioParametrization'}):
    """
    Root element for xCropProtection_config.xml.
    XML:
        <xCropProtection xmlns="urn:xCropProtectionLandscapeScenarioParametrization">
            <PPMCalendars>
                <PPMCalendar include="PPM_Calendar_384.xml"/>
            </PPMCalendars>
            <Technologies include="Technologies.xml"/>
        </xCropProtection>
    """
    PPMCalendars: XCPPPMCalendars = element()
    Technologies: XCPTechnologiesRef = element()

# ==== Technologies XML ====
class XCPTechnologyName(BaseXmlModel, tag='TechnologyName'):
    """TechnologyName element with text content and attributes"""
    value: str
    scales: str = attr(default='global')

class XCPDriftReduction(BaseXmlModel, tag='DriftReduction'):
    """DriftReduction element with text content and attributes"""
    value: Annotated[float, Field(ge=0, le=1)]
    type_attr: str = attr(name='type', default='float')
    unit: str = attr(name='unit', default='1')
    scales: str = attr(default='global')

class XCPTechnology(BaseXmlModel, tag='Technology'):
    """
    Represents a single Technology entry in Technologies.xml.
    XML:
        <Technology>
            <TechnologyName scales="global">Standard</TechnologyName>
            <DriftReduction type="float" unit="1" scales="global">0</DriftReduction>
        </Technology>
    """
    TechnologyName: XCPTechnologyName = element()
    DriftReduction: XCPDriftReduction = element()

class XCPTechnologies(BaseXmlModel, tag='Technologies', nsmap={'': 'urn:xCropProtectionLandscapeScenarioParametrization'}):
    """
    Root element for Technologies.xml.
    """
    Technology: List[XCPTechnology] = element(tag='Technology', default=[])

# ==== PPMCalendar XML ====
class XCPApplicationRate(BaseXmlModel, tag='ApplicationRate'):
    """
    Single application rate with attributes.
    XML: <ApplicationRate type="float" unit="g/ha" scales="global">25</ApplicationRate>
    """
    value: Annotated[float, Field(gt=0)]
    type_attr: str = attr(name='type', default='float')
    unit: str = attr(default='g/ha')
    scales: str = attr(default='global')

class XCPApplicationRates(BaseXmlModel, tag='ApplicationRates'):
    """
    Container for application rates.
    XML:
        <ApplicationRates scales="other/active_substances">
            <ApplicationRate type="float" unit="g/ha" scales="global">25</ApplicationRate>
        </ApplicationRates>
    """
    ApplicationRate: XCPApplicationRate = element()
    scales: str = attr(default='other/active_substances')

class XCPProducts(BaseXmlModel, tag='Products'):
    """
    Products list as comma-separated string.
    XML: <Products type="list[str]" scales="other/active_substances">IMX</Products>
    """
    value: str  # Comma-separated product names
    type_attr: str = attr(name='type', default='list[str]')
    scales: str = attr(default='other/active_substances')

class XCPTank(BaseXmlModel, tag='Tank'):
    """Container for products and application rates."""
    Products: XCPProducts = element()
    ApplicationRates: XCPApplicationRates = element()

class XCPApplicationWindow(BaseXmlModel, tag='ApplicationWindow'):
    """Application date with attributes"""
    value: str
    type_attr: str = attr(name='type', default='xCropProtection.YearDate')
    scales: str = attr(default='global')

class XCPApplicationTechnology(BaseXmlModel, tag='Technology'):
    """Technology name with attributes for Application element"""
    value: str
    scales: str = attr(default='global')

class XCPInCropBuffer(BaseXmlModel, tag='InCropBuffer'):
    """In-crop buffer with attributes"""
    value: Annotated[float, Field(ge=0)]
    type_attr: str = attr(name='type', default='float')
    unit: str = attr(name='unit', default='m')
    scales: str = attr(default='global')

class XCPInFieldMargin(BaseXmlModel, tag='InFieldMargin'):
    """In-field margin with attributes"""
    value: Annotated[float, Field(ge=0)]
    type_attr: str = attr(name='type', default='float')
    unit: str = attr(name='unit', default='m')
    scales: str = attr(default='global')

class XCPMinimumAppliedArea(BaseXmlModel, tag='MinimumAppliedArea'):
    """Minimum applied area with attributes"""
    value: Annotated[float, Field(ge=0)]
    type_attr: str = attr(name='type', default='float')
    unit: str = attr(name='unit', default='m²')
    scales: str = attr(default='global')

class XCPInfectionRate(BaseXmlModel, tag='InfectionRate'):
    """Infection rate with attributes"""
    value: Annotated[float, Field(ge=0, le=1)]
    type_attr: str = attr(name='type', default='float')
    unit: str = attr(name='unit', default='-')
    scales: str = attr(default='global')

class XCPMicroMacroRatio(BaseXmlModel, tag='MicroMacroRatio'):
    """Micro/macro ratio with attributes"""
    value: Annotated[float, Field(ge=0, le=1)]
    type_attr: str = attr(name='type', default='float')
    unit: str = attr(name='unit', default='-')
    scales: str = attr(default='global')

class XCPSmoothingRadiusMicro(BaseXmlModel, tag='SmoothingRadiusMicro'):
    """Smoothing radius micro with attributes"""
    value: Annotated[int, Field(ge=1)]
    type_attr: str = attr(name='type', default='int')
    scales: str = attr(default='global')
    
    @field_validator("value")
    @classmethod
    def must_be_odd(cls, v):
        if v % 2 == 0:
            raise ValueError("SmoothingRadiusMicro must be an odd integer ≥ 1")
        return v

class XCPSmoothingRadiusMacro(BaseXmlModel, tag='SmoothingRadiusMacro'):
    """Smoothing radius macro with attributes"""
    value: Annotated[int, Field(ge=1)]
    type_attr: str = attr(name='type', default='int')
    scales: str = attr(default='global')
    
    @field_validator("value")
    @classmethod
    def must_be_odd(cls, v):
        if v % 2 == 0:
            raise ValueError("SmoothingRadiusMacro must be an odd integer ≥ 1")
        return v

class XCPEdgeBias(BaseXmlModel, tag='EdgeBias'):
    """Edge bias with attributes"""
    value: Annotated[float, Field(gt=0)]
    type_attr: str = attr(name='type', default='float')
    unit: str = attr(name='unit', default='-')
    scales: str = attr(default='global')

class XCPEdgeWidth(BaseXmlModel, tag='EdgeWidth'):
    """Edge width with attributes"""
    value: Annotated[float, Field(gt=0)]
    type_attr: str = attr(name='type', default='float')
    unit: str = attr(name='unit', default='m')
    scales: str = attr(default='global')

class XCPSmoothingFlag(BaseXmlModel, tag='SmoothingFlag'):
    """Smoothing flag with attributes"""
    value: Annotated[int, Field(ge=1, le=2)]
    type_attr: str = attr(name='type', default='int')
    scales: str = attr(default='global')

class XCPApplication(BaseXmlModel, tag='Application'):
    """
    Single application event with all parameters.
    """
    Tank: XCPTank = element()
    ApplicationWindow: XCPApplicationWindow = element()
    Technology: XCPApplicationTechnology = element()
    InCropBuffer: XCPInCropBuffer = element()
    InFieldMargin: XCPInFieldMargin = element()
    MinimumAppliedArea: XCPMinimumAppliedArea = element()
    InfectionRate: XCPInfectionRate = element()
    MicroMacroRatio: XCPMicroMacroRatio = element()
    SmoothingRadiusMicro: XCPSmoothingRadiusMicro = element()
    SmoothingRadiusMacro: XCPSmoothingRadiusMacro = element()
    EdgeBias: XCPEdgeBias = element()
    EdgeWidth: XCPEdgeWidth = element()
    SmoothingFlag: XCPSmoothingFlag = element()

class XCPApplicationSequence(BaseXmlModel, tag='ApplicationSequence'):
    """
    Application sequence with probability as XML attribute.
    XML: <ApplicationSequence probability="1">...</ApplicationSequence>
    """
    probability: Annotated[float, Field(ge=0, le=1)] = attr(default=1.0)
    Application: List[XCPApplication] = element(tag='Application', default=[])

class XCPIndication(BaseXmlModel, tag='Indication'):
    """
    Indication with type attribute.
    XML: <Indication type="xCropProtection.ChoiceDistribution" scales="time/year, space/base_geometry">
    """
    type_attr: str = attr(name='type', default='xCropProtection.ChoiceDistribution')
    scales: str = attr(default='time/year, space/base_geometry')
    ApplicationSequence: List[XCPApplicationSequence] = element(tag='ApplicationSequence', default=[])

class XCPIndications(BaseXmlModel, tag='Indications'):
    """Container for Indication elements."""
    Indication: List[XCPIndication] = element(tag='Indication', default=[])

class XCPTargetFields(BaseXmlModel, tag='TargetFields'):
    """
    Target fields as comma-separated list of integers.
    XML: <TargetFields type="list[int]" scales="global">384,155,122</TargetFields>
    """
    value: str  # Comma-separated field IDs
    type_attr: str = attr(name='type', default='list[int]')
    scales: str = attr(default='global')

class XCPTemporalValidity(BaseXmlModel, tag='TemporalValidity'):
    """
    Temporal validity specification.
    XML: <TemporalValidity scales="time/simulation">always</TemporalValidity>
    """
    value: str = 'always'
    scales: str = attr(default='time/simulation')

class XCPPPMCalendar(BaseXmlModel, tag='PPMCalendar', nsmap={'': 'urn:xCropProtectionLandscapeScenarioParametrization'}):
    """
    Root element for PPM_Calendar_*.xml files.
    """
    TemporalValidity: XCPTemporalValidity = element()
    TargetFields: XCPTargetFields = element()
    Indications: XCPIndications = element()

