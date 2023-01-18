"""Aircraft performance class calculation using BADA 3.15"""
from pathlib import Path
import numpy as np

from airtrafficsim.utils.enums import APSpeedMode, EngineType, Config, FlightPhase, VerticalMode
from airtrafficsim.utils.unit_conversion import Unit


class Bada:
    """
    BADA Performance class 

    Attributes
    ----------
    See __init__()

    Methods
    -------
    __init__:

    add_aircraft_performance:

    Notes
    -----

    """

    def __init__(self):
        """
        Initialize BADA performance parameters 

        Parameters
        ----------
        N: int
            Number of aircrafts. Maximum size of performance array (pre-initialize to eliminate inefficient append)
            TODO: Revise the initial estimate
        """
        # ----------------------------  Operations Performance File (OPF) section 3.11 -----------------------------------------
        # Aircraft type
        self.__n_eng = np.zeros([0])
        """Number of engines"""
        self.__engine_type = np.zeros([0])
        """engine type [Engine_type enum]"""
        self.__wake_category = np.zeros([0], dtype="U1")
        """wake category [Wake_category enum]"""

        # Mass
        self.__m_ref = np.zeros([0])
        """reference mass [tones]"""
        self.m_min = np.zeros([0])
        """minimum mass [tones]"""
        self.__m_max = np.zeros([0])
        """maximum mass [tones]"""
        self.__m_pyld = np.zeros([0])
        """maximum payload mass [tones]"""

        # Flight envelope
        self.v_mo = np.zeros([0])
        """maximum operating speed [knots (CAS)]"""
        self.m_mo = np.zeros([0])
        """maximum operating Mach number [dimensionless]"""
        self.__h_mo = np.zeros([0])
        """maximum opearting altitude [feet]"""
        self.__h_max = np.zeros([0])
        """maximum altitude at MTOW and ISA [feet]"""
        self.__g_w = np.zeros([0])
        """weight gradient on maximum altitude [feet/kg]"""
        self.__g_t = np.zeros([0])
        """temperature gradient on maximum altitude [feet/K]"""

        # Aerodynamics
        self.__S = np.zeros([0])
        """reference wing surface area [m^2]"""
        self.__c_d0_cr = np.zeros([0])
        """parasitic drag coefficient (cruise) [dimensionless]"""
        self.__c_d2_cr = np.zeros([0])
        """induced drag coefficient (cruise) [dimensionless]"""
        self.__c_d0_ap = np.zeros([0])
        """parasitic drag coefficient (approach) [dimensionless]"""
        self.__c_d2_ap = np.zeros([0])
        """induced drag coefficient (approach) [dimensionless]"""
        self.__c_d0_ld = np.zeros([0])
        """parasitic drag coefficient (landing) [dimensionless]"""
        self.__c_d2_ld = np.zeros([0])
        """induced drag coefficient (landing) [dimensionless]"""
        self.__c_d0_ldg = np.zeros([0])
        """parasite darg coefficient (landing gear) [dimensionless]"""
        self.__v_stall_to = np.zeros([0])
        """stall speed (TO) [knots (CAS)]"""
        self.__v_stall_ic = np.zeros([0])
        """stall speed (IC) [knots (CAS)]"""
        self.__v_stall_cr = np.zeros([0])
        """stall speed (CR) [knots (CAS)]"""
        self.__v_stall_ap = np.zeros([0])
        """stall speed (AP) [knots (CAS)]"""
        self.__v_stall_ld = np.zeros([0])
        """stall speed (LD) [knots (CAS)]"""
        self.__c_lbo = np.zeros([0])
        """buffet onset lift coefficient (jet and TBP only) [dimensionless]"""
        self.__k = np.zeros([0])
        """buffeting gradient (Jet & TBP only) [dimensionless]"""

        # Engine thrust
        self.__c_tc_1 = np.zeros([0])
        """1st maximum climb thrust coefficient [Newton (jet/piston) knot-Newton (turboprop)]"""
        self.__c_tc_2 = np.zeros([0])
        """2nd maximum climb thrust coefficient [feet]"""
        self.__c_tc_3 = np.zeros([0])
        """3rd maximum climb thrust coefficient [1/feet^2 (jet) Newton (turboprop) knot-Newton (piston)]"""
        self.__c_tc_4 = np.zeros([0])
        """1st thrust temperature coefficient [K]"""
        self.__c_tc_5 = np.zeros([0])
        """2nd thrust temperature coefficient [1/K]"""
        self.__c_tdes_low = np.zeros([0])
        """low altitude descent thrust coefficient [dimensionless]"""
        self.__c_tdes_high = np.zeros([0])
        """high altitude descent thrust coefficient [dimensionless]"""
        self.__h_p_des = np.zeros([0])
        """transition altitude for calculation of descent thrust [feet]"""
        self.__c_tdes_app = np.zeros([0])
        """approach thrust coefficient [dimensionless]"""
        self.__c_tdes_ld = np.zeros([0])
        """landing thrust coefficient [dimensionless]"""
        self.__v_des_ref = np.zeros([0])
        """reference descent speed [knots (CAS)]"""
        self.__m_des_ref = np.zeros([0])
        """reference descent Mach number [dimensionless]"""

        # Fuel flow
        self.__c_f1 = np.zeros([0])
        """1st thrust specific fuel consumption coefficient [kg/(min*kN) (jet) kg/(min*kN*knot) (turboprop) kg/min (piston)]"""
        self.__c_f2 = np.zeros([0])
        """2nd thrust specific fuel consumption coefficient [knots]"""
        self.__c_f3 = np.zeros([0])
        """1st descent fuel flow coefficient [kg/min]"""
        self.__c_f4 = np.zeros([0])
        """2nd descent fuel flow coefficient [feet]"""
        self.__c_fcr = np.zeros([0])
        """cruise fuel flow correction coefficient [dimensionless]"""

        # Ground movement
        self.__tol = np.zeros([0])
        """take-off length [m]"""
        self.__ldl = np.zeros([0])
        """landing length [m]"""
        self.__span = np.zeros([0])
        """wingspan [m]"""
        self.__length = np.zeros([0])
        """length [m]"""

        # ----------------------------  Airline Procedure Models (APF) section 4 -----------------------------------------
        # Climb
        self.__v_cl_1 = np.zeros([0])
        """standard climb CAS [knots] between 1,500/6,000 and 10,000 ft"""
        self.__v_cl_2 = np.zeros([0])
        """standard climb CAS [knots] between 10,000 ft and Mach transition altitude"""
        self.__m_cl = np.zeros([0])
        """standard climb Mach number above Mach transition altitude"""

        # Cruise
        self.__v_cr_1 = np.zeros([0])
        """standard cruise CAS [knots] between 3,000 and 10,000 ft"""
        self.__v_cr_2 = np.zeros([0])
        """standard cruise CAS [knots] between 10,000 ft and Mach transition altitude"""
        self.__m_cr = np.zeros([0])
        """standard cruise Mach number above Mach transition altitude"""

        # Descent
        self.__v_des_1 = np.zeros([0])
        """standard descent CAS [knots] between 3,000/6,000 and 10,000 ft"""
        self.__v_des_2 = np.zeros([0])
        """standard descent CAS [knots] between 10,000 ft and Mach transition altitude"""
        self.__m_des = np.zeros([0])
        """standard descent Mach number above Mach transition altitude"""

        # Speed schedule
        self.climb_schedule = np.zeros([0, 8])
        """Standard climb CAS schedule [knots*8] (section 4.1)"""
        self.cruise_schedule = np.zeros([0, 5])
        """Standard cruise CAS schedule [knots*5] (section 4.2)"""
        self.descent_schedule = np.zeros([0, 8])
        """Standard descent CAS schedule [knots*8] (section 4.3)"""

        # ----------------------------  Global Aircraft Parameters (GPF) section 5 -----------------------------------------
        # Read data from GPF file (section 6.8)
        # 'CD', 1X, A15, 1X, A7, 1X, A16, 1x, A29, 1X, E10.5
        if Path(__file__).parent.parent.parent.parent.resolve().joinpath('./data/performance/BADA/BADA.GPF').is_file():
            GPF = np.genfromtxt(Path(__file__).parent.parent.parent.parent.resolve().joinpath('./data/performance/BADA/BADA.GPF'),
                                delimiter=[3, 16, 8, 17, 29, 12], dtype="U2,U15,U7,U16,U29,f8", comments="CC", autostrip=True, skip_footer=1)

            # Maximum acceleration
            self.__A_L_MAX_CIV = GPF[0][5]
            """Maximum longitudinal acceleration for civil flights [2 ft/s^2]"""
            self.__A_N_MAX_CIV = GPF[1][5]
            """Maximum normal acceleration for civil flights [5 ft/s^2]"""

            # Bank angles
            self.__PHI_NORM_CIV_TOLD = GPF[2][5]
            """Nominal bank angles fpr civil flight during TO and LD [15 deg]"""
            self.__PHI_NORM_CIV_OTHERS = GPF[3][5]
            """Nominal bank angles for civil flight during all other phases [30 deg]"""
            self.__PHI_NORM_MIL = GPF[4][5]
            """Nominal bank angles for military flight (all phases) [50 deg]"""
            self.__PHI_MAX_CIV_TOLD = GPF[5][5]
            """Maximum bank angles for civil flight during TO and LD [25 deg]"""
            self.__PHI_MAX_CIV_HOLD = GPF[6][5]
            """Maximum bank angles for civil flight during HOLD [35 deg]"""
            self.__PHI_MAX_CIV_OTHERS = GPF[7][5]
            """Maximum bank angles for civil flight during all other phases [45 deg]"""
            self.__PHI_MAX_MIL = GPF[8][5]
            """Maximum bank angles for military flight (all phases) [70 deg]"""

            # Expedited descent (drag multiplication factor during expedited descent to simulate use of spoilers)
            self.__C_DES_EXP = GPF[9][5]
            """Expedited descent factor [1.6]"""

            # Thrust factors
            self.__C_TCR = GPF[11][5]
            """Maximum cruise thrust coefficient [0.95] (postition different between GPF and user menu)"""
            self.__C_TH_TO = GPF[10][5]
            """Take-off thrust coefficient [1.2] (no longer used since BADA 3.0) (postition different between GPF and user menu)"""

            # Configuration altitude threshold
            self.__H_MAX_TO = GPF[12][5]
            """Maximum altitude threshold for take-off [400 ft]"""
            self.__H_MAX_IC = GPF[13][5]
            """Maximum altitude threshold for initial climb [2,000 ft]"""
            self.__H_MAX_AP = GPF[14][5]
            """Maximum altitude threshold for approach [8,000 ft]"""
            self.__H_MAX_LD = GPF[15][5]
            """Maximum altitude threshold for landing [3,000 ft]"""

            # Minimum speed coefficient
            self.__C_V_MIN = GPF[16][5]
            """Minimum speed coefficient (all other phases) [1.3]"""
            self.__C_V_MIN_TO = GPF[17][5]
            """Minimum speed coefficient for take-off [1.2]"""

            # Speed schedules
            self.__V_D_CL_1 = GPF[18][5]
            """Climb speed increment below 1,500 ft (jet) [5 knot CAS]"""
            self.__V_D_CL_2 = GPF[19][5]
            """Climb speed increment below 3,000 ft (jet) [10 knot CAS]"""
            self.__V_D_CL_3 = GPF[20][5]
            """Climb speed increment below 4,000 ft (jet) [30 knot CAS]"""
            self.__V_D_CL_4 = GPF[21][5]
            """Climb speed increment below 5,000 ft (jet) [60 knot CAS]"""
            self.__V_D_CL_5 = GPF[22][5]
            """Climb speed increment below 6,000 ft (jet) [80 knot CAS]"""
            self.__V_D_CL_6 = GPF[23][5]
            """Climb speed increment below 500 ft (turbo/piston) [20 knot CAS]"""
            self.__V_D_CL_7 = GPF[24][5]
            """Climb speed increment below 1,000 ft (turbo/piston) [30 knot CAS]"""
            self.__V_D_CL_8 = GPF[25][5]
            """ Climb speed increment below 1,500 ft (turbo/piston) [35 knot CAS]"""
            self.__V_D_DSE_1 = GPF[26][5]
            """Descent speed increment below 1,000 ft (jet/turboprop) [5 knot CAS]"""
            self.__V_D_DSE_2 = GPF[27][5]
            """Descent speed increment below 1,500 ft (jet/turboprop) [10 knot CAS]"""
            self.__V_D_DSE_3 = GPF[28][5]
            """Descent speed increment below 2,000 ft (jet/turboprop) [20 knot CAS]"""
            self.__V_D_DSE_4 = GPF[29][5]
            """Descent speed increment below 3,000 ft (jet/turboprop) [50 knot CAS]"""
            self.__V_D_DSE_5 = GPF[30][5]
            """Descent speed increment below 500 ft (piston) [5 knot CAS]"""
            self.__V_D_DSE_6 = GPF[31][5]
            """Descent speed increment below 1,000 ft (piston) [10 knot CAS]"""
            self.__V_D_DSE_7 = GPF[32][5]
            """Descent speed increment below 1,500 ft (piston) [20 knot CAS]"""

            # Holding speeds
            self.__V_HOLD_1 = GPF[33][5]
            """Holding speed below FL140 [230 knot CAS]"""
            self.__V_HOLD_2 = GPF[34][5]
            """Holding speed between FL140 and FL220 [240 knot CAS]"""
            self.__V_HOLD_3 = GPF[35][5]
            """Holding speed between FL220 and FL340 [265 knot CAS]"""
            self.__V_HOLD_4 = GPF[36][5]
            """Holding speed above FL340 [0.83 Mach]"""

            # Ground speed
            self.__V_BACKTRACK = GPF[37][5]
            """Runway backtrack speed [35 knot CAS]"""
            self.__V_TAXI = GPF[38][5]
            """Taxi speed [15 knot CAS]"""
            self.__V_APRON = GPF[39][5]
            """Apron speed [10 knot CAS]"""
            self.__V_GATE = GPF[40][5]
            """Gate speed [5 knot CAS]"""

            # Reduced power coefficient
            self.__C_RED_TURBO = GPF[42][5]
            """Maximum reduction in power for turboprops [0.25] (postition different between GPF and user menu)"""
            self.__C_RED_PISTON = GPF[41][5]
            """Maximum reduction in power for pistons [0.0] (postition different between GPF and user menu)"""
            self.__C_RED_JET = GPF[43][5]
            """Maximum reduction in power for jets [0.15]"""

            # Delete variable to free memory
            del GPF

        else:
            print("BADA.GPF File does not exit")

        # ----------------------------  Atmosphere model section 3.1 -----------------------------------------
        # MSL Standard atmosphere condition (section 3.1.1)
        self.__T_0 = 288.15
        """Standard atmospheric temperature at MSL [K]"""
        self.__P_0 = 101325
        """Standard atmospheric pressure at MSL [Pa]"""
        self.__RHO_0 = 1.225
        """Standard atmospheric density at MSL [kg/m^3]"""
        self.__A_0 = 340.294
        """Speed of sound [m/s]"""

        # Expression (section 3.1.2)
        self.__KAPPA = 1.4
        """Adiabatic index of air [dimensionless]"""
        self.__R = 287.05287
        """Real gas constant of air [m^2/(K*s^2)]"""
        self.__G_0 = 9.80665
        """Gravitational acceleration [m/s^2]"""
        self.__BETA_T_BELOW_TROP = -0.0065
        """ISA temperature gradient with altitude below the tropopause [K/m]"""

        # Tropopause (separation between troposphere (below) and stratosphere (above))
        self.__H_P_TROP = 11000
        """Geopotential pressure altitude [m]"""

        # ----------------------------  SYNONYM FILE FORMAT (SYNONYM.NEW) section 6.3 -----------------------------------------
        # | 'CD' | SUPPORT TYPE (-/*) | AIRCRAFT Code | MANUFACTURER | NAME OR MODEL | FILE NAME | ICAO (Y/N) |
        self.__SYNONYM = np.genfromtxt(Path(__file__).parent.parent.parent.parent.resolve().joinpath('./data/performance/BADA/SYNONYM.NEW'), delimiter=[3, 2, 7, 20, 25, 8, 5], names=[
                                       'CD', 'ST', 'ACCODE', 'MANUFACTURER', 'MODEL', 'FILENAME', 'ICAO'], dtype="U2,U1,U4,U18,U25,U6,U1", comments="CC", autostrip=True, skip_footer=1, encoding='unicode_escape')

    def add_aircraft(self, icao, mass_class=2):
        """
        Add one specific aircraft performance data to the performance array according to index.

        Parameters
        ----------
        self: Performance class instance
            Used to add data to the performance array.

        ICAO: string
            ICAO code of the specific aircraft.

        mass: int
            Mass of aircraft [kg]

        mass_class: int
            Aircraft mass for specific flight. To be used for APF. 1 = LO, 2 = AV, 3 = HI TODO: useful?

        Returns
        -------
        TODO:
        """

        # Get file name by searching in SYNONYM.NEW
        row = np.where(self.__SYNONYM['ACCODE'] == icao)[
            0][0]      # Get row index
        file_name = self.__SYNONYM[row][5]

        if(not file_name):
            print("No aircraft in SYNONYM.NEW")

        # Get data from Operations Performance File (Section 6.4)
        OPF = np.genfromtxt(Path(__file__).parent.parent.parent.parent.resolve().joinpath('./data/performance/BADA/', file_name+'.OPF'), delimiter=[
                            3, 2, 2, 13, 13, 13, 13, 11], dtype="U2,U1,U2,f8,f8,f8,f8,f8", comments="CC", autostrip=True, skip_header=16, skip_footer=1)

        # 'CD', 3X, A6, 9X, I1, 12X, A9, 17X, A1 - aircraft type block - 1 data line
        # | 'CD' | ICAO | # of engine | 'engines' | engine type ( Jet,  Turboprop  or  Piston) | wake category ( J (jumbo), H (heavy), M (medium) or L (light))
        OPF_Actype = np.genfromtxt(Path(__file__).parent.parent.parent.parent.resolve().joinpath(
            './data/performance/BADA/', file_name+'.OPF'), delimiter=[5, 15, 1, 12, 26, 1], dtype="U2,U6,i1,U7,U9,U1", comments="CC", autostrip=True, max_rows=1)

        # Get data from Airlines Procedures File (Section 6.5)
        # 'CD', 25X, 2(I3, 1X), I2, 10X, 2(Ix, 1X), I2, 2X, I2, 2(1X, I3) - procedures specification block - 3 dataline
        APF = np.genfromtxt(Path(__file__).parent.parent.parent.parent.resolve().joinpath('./data/performance/BADA/', file_name+'.APF'), delimiter=[
                            6, 8, 9, 4, 4, 4, 3, 5, 4, 4, 4, 4, 3, 4, 4, 5, 4, 4, 4, 5, 7], dtype="U2,U7,U7,U2,i2,i2,i2,i2,i2,i2,i2,i2,i2,i2,i2,i2,i2,i2,i2,i2,U6", comments="CC", autostrip=True)

        self.__n_eng = np.append(self.__n_eng, OPF_Actype.item()[2])
        self.__engine_type = np.append(self.__engine_type, {
                                       'Jet': 1, 'Turboprop': 2, 'Piston': 3}.get(OPF_Actype.item()[4]))
        self.__wake_category = np.append(
            self.__wake_category, OPF_Actype.item()[5])
        self.__m_ref = np.append(self.__m_ref, OPF[0][3])
        self.m_min = np.append(self.m_min, OPF[0][4])
        self.__m_max = np.append(self.__m_max, OPF[0][5])
        self.__m_pyld = np.append(self.__m_pyld, OPF[0][6])
        self.v_mo = np.append(self.v_mo, OPF[1][3])
        self.m_mo = np.append(self.m_mo, OPF[1][4])
        self.__h_mo = np.append(self.__h_mo, OPF[1][5])
        self.__h_max = np.append(self.__h_max, OPF[1][6])
        self.__g_w = np.append(self.__g_w, OPF[0][7])
        self.__g_t = np.append(self.__g_t, OPF[1][7])
        self.__S = np.append(self.__S, OPF[2][3])
        self.__c_d0_cr = np.append(self.__c_d0_cr, OPF[3][5])
        self.__c_d2_cr = np.append(self.__c_d2_cr, OPF[3][6])
        self.__c_d0_ap = np.append(self.__c_d0_ap, OPF[6][5])
        self.__c_d2_ap = np.append(self.__c_d2_ap, OPF[6][6])
        self.__c_d0_ld = np.append(self.__c_d0_ld, OPF[7][5])
        self.__c_d2_ld = np.append(self.__c_d2_ld, OPF[7][6])
        self.__c_d0_ldg = np.append(self.__c_d0_ldg, OPF[11][5])
        self.__v_stall_to = np.append(self.__v_stall_to, OPF[5][4])
        self.__v_stall_ic = np.append(self.__v_stall_ic, OPF[4][4])
        self.__v_stall_cr = np.append(self.__v_stall_cr, OPF[3][4])
        self.__v_stall_ap = np.append(self.__v_stall_ap, OPF[6][4])
        self.__v_stall_ld = np.append(self.__v_stall_ld, OPF[7][4])
        self.__c_lbo = np.append(self.__c_lbo, OPF[2][4])
        self.__k = np.append(self.__k, OPF[2][5])
        self.__c_tc_1 = np.append(self.__c_tc_1, OPF[14][3])
        self.__c_tc_2 = np.append(self.__c_tc_2, OPF[14][4])
        self.__c_tc_3 = np.append(self.__c_tc_3, OPF[14][5])
        self.__c_tc_4 = np.append(self.__c_tc_4, OPF[14][6])
        self.__c_tc_5 = np.append(self.__c_tc_5, OPF[14][7])
        self.__c_tdes_low = np.append(self.__c_tdes_low, OPF[15][3])
        self.__c_tdes_high = np.append(self.__c_tdes_high, OPF[15][4])
        self.__h_p_des = np.append(self.__h_p_des, OPF[15][5])
        self.__c_tdes_app = np.append(self.__c_tdes_app, OPF[15][6])
        self.__c_tdes_ld = np.append(self.__c_tdes_ld, OPF[15][7])
        self.__v_des_ref = np.append(self.__v_des_ref, OPF[16][3])
        self.__m_des_ref = np.append(self.__m_des_ref, OPF[16][4])
        self.__c_f1 = np.append(self.__c_f1, OPF[17][3])
        self.__c_f2 = np.append(self.__c_f2, OPF[17][4])
        self.__c_f3 = np.append(self.__c_f3, OPF[18][3])
        self.__c_f4 = np.append(self.__c_f4, OPF[18][4])
        self.__c_fcr = np.append(self.__c_fcr, OPF[19][3])
        self.__tol = np.append(self.__tol, OPF[20][3])
        self.__ldl = np.append(self.__ldl, OPF[20][4])
        self.__span = np.append(self.__span, OPF[20][5])
        self.__length = np.append(self.__length, OPF[20][6])
        self.__v_cl_1 = np.append(self.__v_cl_1, APF[mass_class][4])
        self.__v_cl_2 = np.append(self.__v_cl_2, APF[mass_class][5])
        self.__m_cl = np.append(self.__m_cl, APF[mass_class][6]/100)
        self.__v_cr_1 = np.append(self.__v_cr_1, APF[mass_class][9])
        self.__v_cr_2 = np.append(self.__v_cr_2, APF[mass_class][10])
        self.__m_cr = np.append(self.__m_cr, APF[mass_class][11]/100)
        self.__v_des_1 = np.append(self.__v_des_1, APF[mass_class][14])
        self.__v_des_2 = np.append(self.__v_des_2, APF[mass_class][13])
        self.__m_des = np.append(self.__m_des, APF[mass_class][12]/100)
        self.climb_schedule = np.append(
            self.climb_schedule, [[0., 0., 0., 0., 0., 0., 0., 0.]], axis=0)
        self.cruise_schedule = np.append(
            self.cruise_schedule, [[0., 0., 0., 0., 0.]], axis=0)
        self.descent_schedule = np.append(
            self.descent_schedule, [[0., 0., 0., 0., 0., 0., 0., 0.]], axis=0)

        # Delete variable to free memory
        del APF
        del OPF_Actype
        del OPF

    def del_aircraft(self, index):
        """
        Delete one specific aircraft performance data to the performance array according to index. This is done by setting all parameters to 0 for reuse in future.

        Parameters
        ----------
        self: Performance class instance
            Used to delete data to the performance array.

        index: int
            Index of array.
        """
        self.__n_eng = np.delete(self.__n_eng, index)
        self.__engine_type = np.delete(self.__engine_type, index)
        self.__wake_category = np.delete(self.__wake_category, index)
        self.__m_ref = np.delete(self.__m_ref, index)
        self.m_min = np.delete(self.m_min, index)
        self.__m_max = np.delete(self.__m_max, index)
        self.__m_pyld = np.delete(self.__m_pyld, index)
        self.v_mo = np.delete(self.v_mo, index)
        self.m_mo = np.delete(self.m_mo, index)
        self.__h_mo = np.delete(self.__h_mo, index)
        self.__h_max = np.delete(self.__h_max, index)
        self.__g_w = np.delete(self.__g_w, index)
        self.__g_t = np.delete(self.__g_t, index)
        self.__S = np.delete(self.__S, index)
        self.__c_d0_cr = np.delete(self.__c_d0_cr, index)
        self.__c_d2_cr = np.delete(self.__c_d2_cr, index)
        self.__c_d0_ap = np.delete(self.__c_d0_ap, index)
        self.__c_d2_ap = np.delete(self.__c_d2_ap, index)
        self.__c_d0_ld = np.delete(self.__c_d0_ld, index)
        self.__c_d2_ld = np.delete(self.__c_d2_ld, index)
        self.__c_d0_ldg = np.delete(self.__c_d0_ldg, index)
        self.__v_stall_to = np.delete(self.__v_stall_to, index)
        self.__v_stall_ic = np.delete(self.__v_stall_ic, index)
        self.__v_stall_cr = np.delete(self.__v_stall_cr, index)
        self.__v_stall_ap = np.delete(self.__v_stall_ap, index)
        self.__v_stall_ld = np.delete(self.__v_stall_ld, index)
        self.__c_lbo = np.delete(self.__c_lbo, index)
        self.__k = np.delete(self.__k, index)
        self.__c_tc_1 = np.delete(self.__c_tc_1, index)
        self.__c_tc_2 = np.delete(self.__c_tc_2, index)
        self.__c_tc_3 = np.delete(self.__c_tc_3, index)
        self.__c_tc_4 = np.delete(self.__c_tc_4, index)
        self.__c_tc_5 = np.delete(self.__c_tc_5, index)
        self.__c_tdes_low = np.delete(self.__c_tdes_low, index)
        self.__c_tdes_high = np.delete(self.__c_tdes_high, index)
        self.__h_p_des = np.delete(self.__h_p_des, index)
        self.__c_tdes_app = np.delete(self.__c_tdes_app, index)
        self.__c_tdes_ld = np.delete(self.__c_tdes_ld, index)
        self.__v_des_ref = np.delete(self.__v_des_ref, index)
        self.__m_des_ref = np.delete(self.__m_des_ref, index)
        self.__c_f1 = np.delete(self.__c_f1, index)
        self.__c_f2 = np.delete(self.__c_f2, index)
        self.__c_f3 = np.delete(self.__c_f3, index)
        self.__c_f4 = np.delete(self.__c_f4, index)
        self.__c_fcr = np.delete(self.__c_fcr, index)
        self.__tol = np.delete(self.__tol, index)
        self.__ldl = np.delete(self.__ldl, index)
        self.__span = np.delete(self.__span, index)
        self.__length = np.delete(self.__length, index)
        self.__v_cl_1 = np.delete(self.__v_cl_1, index)
        self.__v_cl_2 = np.delete(self.__v_cl_2, index)
        self.__m_cl = np.delete(self.__m_cl, index)
        self.__v_cr_1 = np.delete(self.__v_cr_1, index)
        self.__v_cr_2 = np.delete(self.__v_cr_2, index)
        self.__m_cr = np.delete(self.__m_cr, index)
        self.__v_des_1 = np.delete(self.__v_des_1, index)
        self.__v_des_2 = np.delete(self.__v_des_2, index)
        self.__m_des = np.delete(self.__m_des, index)
        self.climb_schedule = np.delete(self.climb_schedule, index, axis=0)
        self.cruise_schedule = np.delete(self.cruise_schedule, index, axis=0)
        self.descent_schedule = np.delete(self.descent_schedule, index, axis=0)

    def cal_fuel_burn(self, flight_phase, tas, thrust, alt):
        """
        Calculate fuel burn

        Parameters
        ----------
        flight_phase : float[]
            Flight phase from Traffic class [Flight_phase enum]
        tas : float[]
            True airspeed [kt]
        thrust : float[]
            Thrust [N]
        alt : _type_
            Altitude [ft]

        Returns
        -------
        Fuel burn : float[]
            Fuel burn [kg/s]

        TODO: Thrust mode -> idle descent
        """
        a = self.__cal_nominal_fuel_flow(tas, thrust)/60.0
        return np.select(
            condlist=[
                flight_phase == FlightPhase.CRUISE,
                flight_phase == FlightPhase.DESCENT,
                flight_phase == FlightPhase.APPROACH,
                flight_phase == FlightPhase.LANDING
            ],
            choicelist=[
                self.__cal_cruise_fuel_flow(
                    tas, thrust)/60000.0,                      # cruise
                # Idle descent
                self.__cal_minimum_fuel_flow(alt)/60000.0,
                self.__cal_approach_landing_fuel_flow(
                    tas, thrust, alt)/60000.0,       # Approach
                self.__cal_approach_landing_fuel_flow(
                    tas, thrust, alt/60000.0)        # Landing
            ],
            default=self.__cal_nominal_fuel_flow(
                tas, thrust)/60000.0                      # Others
        )

    def cal_thrust(self, vertical_mode, configuration, H_p, V_tas, d_T, drag, ap_speed_mode):
        """
        Calculate thrust given flight phases.

        Parameters
        ----------
        vertical_mode : float[]
            Vertical mode from Traffic class [Vertical_mode enum]

        configuration : float[] 
            Configuration from Traffic class [Configuration enum]

         H_p : float[]
            Geopotential pressuer altitude [ft]

        V_tas : float[]
            True airspeed [kt]

        d_T : float[]
            Temperature differential from ISA [K]

        drag : float[]
            Drag forces [N]

        ap_speed_mode : AP_speed_mode enum []
            Autopilot speed mode [1: Constant CAS, 2: Constant Mach, 3: Acceleration, 4: Deceleration]

        Returns
        -------
        _type_
            _description_
        """
        return np.select(
            condlist=[
                        (vertical_mode == VerticalMode.CLIMB) | (
                            (vertical_mode == VerticalMode.LEVEL) & (ap_speed_mode == APSpeedMode.ACCELERATE)),
                        (vertical_mode == VerticalMode.LEVEL) & ((ap_speed_mode == APSpeedMode.CONSTANT_CAS) | (
                            ap_speed_mode == APSpeedMode.CONSTANT_MACH)),
                        (vertical_mode == VerticalMode.DESCENT) | ((vertical_mode == VerticalMode.LEVEL) & (ap_speed_mode == APSpeedMode.DECELERATE))],
            choicelist=[
                self.__cal_max_climb_to_thrust(H_p, V_tas, d_T),
                # max climb thrust when acceleration, T = D at cruise, but limited at max cruise thrust
                np.minimum(drag, self.__cal_max_cruise_thrust(
                    self.__cal_max_climb_to_thrust(H_p, V_tas, d_T))),
                self.__cal_descent_thrust(H_p, self.__cal_max_climb_to_thrust(H_p, V_tas, d_T), configuration)])

    # -----------------------------------------------------------------------------------------------------
    # ----------------------------- BADA Implementation----------------------------------------------------
    # -----------------------------------------------------------------------------------------------------

    # ----------------------------  Mass section 3.4 -----------------------------------------

    def __cal_operating_speed(self, m, V_ref):
        """
        Calculate operating speed given mass (Equation 3.4-1)

        Parameters
        ----------
        m: float[]
            Aircraft mass [kg]

        v_ref: float[]
            Velocity reference (e.g. v_stall) [m/s] 

        Returns
        -------
        V: float[]
            Operating velocity [m/s]
        """
        return V_ref * np.sqrt(m/(self.__m_ref*1000.0))

    # ----------------------------  Flight envelope section 3.5 -----------------------------------------

    def cal_maximum_altitude(self, d_T, m):
        """
        Calculate flight envelope (Section 3.5-1)

        Parameters
        ----------
        d_T: float[]
            Temperature differential from ISA [K]

        m: float[]
            Aircraft mass [kg]

        Returns
        -------
        h_max/act: float[]
            Actual maximum altitude for any given mass [ft]
        """
        return np.where(self.__h_max == 0,
                        # If h_max in OPF file is zero, maximum altitude is always h_MO
                        self.__h_mo,
                        # Else Equation 3.5-1
                        np.minimum(self.__h_mo, self.__h_max + self.__g_t*(d_T-self.__c_tc_4) + self.__g_w*(self.__m_max-m)))

    def cal_minimum_speed(self, configuration):
        """
        Calculate minimum speed for aircraft (3.5-2~3)

        Parameters
        ----------
        configuration: float[]
            configuration from Traffic class [configuration enum]

        Returns
        -------
        v_min: float[]
            Minimum at speed at specific configuration [knots] TODO: need to consider mass using __calculate_operating_speed?
        """

        return np.select(condlist=[configuration == Config.TAKEOFF,
                                   configuration == Config.INITIAL_CLIMB,
                                   configuration == Config.APPROACH,
                                   configuration == Config.LANDING],

                         choicelist=[self.__C_V_MIN_TO * self.__v_stall_to,
                                     self.__C_V_MIN * self.__v_stall_ic,
                                     self.__C_V_MIN * self.__v_stall_ap,
                                     self.__C_V_MIN * self.__v_stall_ld],

                         default=self.__C_V_MIN * self.__v_stall_cr)

    # ----------------------------  Aerodynamic section 3.6 -----------------------------------------

    def cal_aerodynamic_drag(self, V_tas, bank_angle, m, rho, configuration, c_des_exp):
        """
        Calculate Aerodynamic drag (Section 3.6.1)

        Parameters
        ----------
        V_tas: float[]
            True airspeed [m/s]

        bank_angles: float[]
            Bank angles from Traffic class [deg]

        m: float[]
            Aircraft mass [kg]

        rho: float[]
            Density [kg/m^3]

        configuration: float[]
            Configuration from Traffic class [Configuration enum]

        c_des_exp: float[]
            Coefficient of expedited descent factor [dimensionless]

        Returns
        -------
        D: float[]
            Drag force [N]
        """
        # Lift coefficient (Equation 3.6-1)
        c_L = 2.0 * m * self.__G_0 / rho / \
            np.square(V_tas) / self.__S / np.cos(np.deg2rad(bank_angle))

        # Drag coefficient (Equation3.6-2~4)
        c_D = np.select(condlist=[
            configuration == Config.APPROACH,
            configuration == Config.LANDING
        ],
            choicelist=[
            np.where(self.__c_d2_ap != 0,                                               # Approach config
                     # If c_d0_ap / c_d2_ap are NOT set to 0 (Equation 3.6-3)
                     self.__c_d0_ap + self.__c_d2_ap * \
                     np.square(c_L),
                     self.__c_d0_cr + self.__c_d2_cr * np.square(c_L)),                          # If c_d0_ap / c_d2_ap are  set to 0 (Equation 3.6-2)
            np.where(self.__c_d2_ld != 0,                                               # Landing config
                     # If c_d0_ld / c_d2_ld are NOT set to 0 (Equation 3.6-4)
                     self.__c_d0_ld + self.__c_d0_ldg + \
                     self.__c_d2_ld * np.square(c_L),
                     self.__c_d0_cr + self.__c_d2_cr * np.square(c_L))                           # If c_d0_ld / c_d2_ld are set to 0 (Equation 3.6-2)
        ],
            # All configs except for approach and landing. (Equation 3.6-2)
            default=self.__c_d0_cr + \
            self.__c_d2_cr * np.square(c_L),
        )

        # Drag force
        return np.where(V_tas == 0.0, 0.0, c_D * rho * np.square(V_tas) * self.__S / 2.0 * c_des_exp)

    def cal_low_speed_buffeting_limit(self, p, M, m):
        """
        Low speed buffeting limit for jet and turboprop aircraft. It is expressed as Mach number. (Equation 3.6-6)
        TODO: Appendix B

        Parameters
        ----------
        p: float[]
            Pressure [Pa] 

        M: float[]
            Mach number [dimensionless]

        m: float[]
            Aircraft mass [kg]

        Returns
        -------
        M: float[]
            Mach number [dimensionless]

        Notes
        -----
        TODO: Calculate minimum speed for Jet and Turboprop when H_p >= 15000. V_min = MAX(V_min_stall, M_b) (<- same unit)
              If H_p < 15000, V_min = V_min_stall
        """
        Q = (-np.square(-self.__c_lbo/self.__k)/9.0)
        R = (-27.0*(m*self.__G_0/self.__S)/0.583/p/self.__k -
             2.0*np.power(-self.__c_lbo/self.__k, 3)) / 54.0
        theta = np.arccos(R/np.sqrt(-np.power(Q, 3)))

        X_1 = 2.0 * np.sqrt(-Q) * np.cos(np.deg2rad(theta/3)
                                         ) + (self.__c_lbo/self.__k)/3.0
        X_2 = 2.0 * np.sqrt(-Q) * np.cos(np.deg2rad(theta /
                                                    3 + 120)) + (self.__c_lbo/self.__k)/3.0
        X_3 = 2.0 * np.sqrt(-Q) * np.cos(np.deg2rad(theta /
                                                    3 + 240)) + (self.__c_lbo/self.__k)/3.0

        arr = np.array([X_1, X_2, X_3])
        return np.max(np.where(arr <= 0, np.inf, arr), axis=0)

    # ----------------------------  Engine Thrust section 3.7 -----------------------------------------

    def __cal_max_climb_to_thrust(self, H_p, V_tas, d_T):
        """
        Calculate maximum climb thrust for both take-off and climb phases (Section 3.7.1)

        Parameters
        ----------
        H_p: float[]
            Geopotential pressuer altitude [ft] TODO: Different unit

        V_tas: float[]
            True airspeed [kt] TODO: Different unit

        d_T: float[]
            Temperature differential from ISA [K]

        Returns
        -------
        Thr_max_climb: float[]
            Maximum climb thrust [N]
        """
        # Maximum climb thrust at standard atmosphere conditions (Equations 3.7-1~3)
        thr_max_climb_isa = np.select([self.__engine_type == EngineType.JET,
                                       self.__engine_type == EngineType.TURBOPROP,
                                       self.__engine_type == EngineType.PISTON],

                                      [self.__c_tc_1 * (1.0 - H_p/self.__c_tc_2 + self.__c_tc_3 * np.square(H_p)),
                                       self.__c_tc_1/V_tas *
                                       (1.0 - H_p/self.__c_tc_2) + self.__c_tc_3,
                                       self.__c_tc_1 *
                                       (1.0 - H_p/self.__c_tc_2) +
                                       self.__c_tc_3/V_tas
                                       ])

        # Corrected for temperature deviation from ISA
        return thr_max_climb_isa * (1.0 - np.clip(np.clip(self.__c_tc_5, 0.0, None) * (d_T-self.__c_tc_4), 0.0, 0.4))

    def __cal_max_cruise_thrust(self, Thr_max_climb):
        """
        Calculate maximum cruise thrust (Equation 3.7-8)

        Parameters
        ----------
        Thr_max_climb: float[]
            Maximum climb thrust [N] (obtained from cal_max_climb_to_thrust())

        Returns
        -------
        thr_cruise_max: float[]
            Maximum cruise thrust [N]

        Notes
        -----
        The normal cruise thrust is by definition set equal to drag (Thr=D). However, the maximum amount of thrust available in cruise situation is limited.
        """
        return self.__C_TCR * Thr_max_climb

    def __cal_descent_thrust(self, H_p, Thr_max_climb, configuration):
        """
        Calculate descent thrust (Section 3.7.3)

        Parameters
        ----------
        H_p: float[]
            Geopotential pressuer altitude [m]

        Thr_max_climb: float[]
            Maximum climb thrust [N]

        Configuration: float[]
            Configuration from Traffic class [Configuration enum]

        Returns
        -------
        Thr_des: float[]
            Descent thrust [N]
        """
        # When “non-clean” data (see Section 3.6.1) is available, H_p,des cannot be below H_max,AP.
        return np.where(H_p > np.where(self.__c_d2_ap != 0, np.clip(self.__h_p_des, self.__H_MAX_AP, None), self.__h_p_des),
                        # If H_p > H_p_des
                        self.__c_tdes_high * Thr_max_climb,     # Equation 3.7-9
                        # Else
                        np.select([configuration == Config.CLEAN,
                                   configuration == Config.APPROACH,
                                   configuration == Config.LANDING],

                                  [self.__c_tdes_low * Thr_max_climb,       # Equation 3.7-10
                                   self.__c_tdes_app * Thr_max_climb,       # Equation 3.7-11
                                   self.__c_tdes_ld * Thr_max_climb]))      # Equation 3.7-12

    # ----------------------------  Reduced climb power section 3.8 -----------------------------------------

    def cal_reduced_climb_power(self, m, H_p, H_max):
        """
        Calculate reduced climb power (section 3.8)

        Parameters
        ----------
        m: float[]
            Aircraft mass [kg]

        H_p: float[]
            Geopotential pressuer altitude [m]

        H_max: float[]
            Actual maximum altitude for any given mass [kg] (obtained from __cal_maximum_altitude())

        Returns
        -------
        C_pow,red: float[]
            Coefficient of reduced climb power [dimensionless]

        Notes
        -----
        The result can be applied in the calculation of ROCD during climb phase TODO:
        """
        c_red = np.where(H_p < 0.8*H_max,
                         # If (H_p < 0.8*H_max) section 5.11
                         np.select([self.__engine_type == EngineType.TURBOPROP, self.__engine_type == EngineType.PISTON, self.__engine_type == EngineType.JET],
                                   [self.__C_RED_TURBO, self.__C_RED_PISTON, self.__C_RED_JET]),
                         # Else
                         0.0)

        # Equation 3.8-1
        return 1.0 - c_red * (self.__m_max - m/1000.0) / (self.__m_max - self.m_min)

    # ----------------------------  Fuel consumption section 3.9 -----------------------------------------

    def __cal_nominal_fuel_flow(self, V_tas, Thr):
        """
        Calculate nominal fuel flow (except idle descent and cruise) (equations 3.9-1~3 and 3.9-7)

        Parameters
        ----------
        V_tas: float[]
            True airspeed [kt] TODO: Different unit

        Thr: float[]
            Thrust acting parallel to the aircraft velocity vector [N]

        Returns
        -------
        f_norm: float[]
            Nominal fuel flow [kg/min]
        """
        return np.select([self.__engine_type == EngineType.JET,
                          self.__engine_type == EngineType.TURBOPROP,
                          self.__engine_type == EngineType.PISTON],

                         [self.__c_f1 * (1.0 + V_tas/self.__c_f2) * Thr,                    # Equation 3.9-1 and 3.9-3
                          # Equation 3.9-2 and 3.9-3
                          self.__c_f1 * (1.0 - V_tas/self.__c_f2) * \
                          (V_tas/1000.0) * Thr,
                          self.__c_f1])                                                     # Equation 3.9-7

    def __cal_minimum_fuel_flow(self, H_p):
        """
        Calculate fuel flow for idle descent (equations 3.9-4 and 3.9-8)

        Parameters
        ----------
        H_p: float[]
            Geopotential pressuer altitude [ft] TODO: Different uni

        Returns
        -------
        f_min: float[]
            Minimum fuel flow [kg/min]
        """
        return np.where(self.__engine_type != EngineType.PISTON,
                        # Non piston
                        # Equation 3.9-4
                        self.__c_f3 * (1.0 - H_p/self.__c_f4),
                        # Piston
                        self.__c_f3)                                # Equation 3.9-8

    def __cal_approach_landing_fuel_flow(self, V_tas, Thr, H_p):
        """
        Calculate fuel flow for approach and landing (equations 3.9-5 and 3.9-8)

        Parameters
        ----------
        V_tas: float[]
            True airspeed [kt] TODO: Different unit

        Thr: float[]
            Thrust acting parallel to the aircraft velocity vector [N]

        H_p: float[]
            Geopotential pressuer altitude [ft] TODO: Different uni

        Returns
        -------
        f_app/ld: float[]
            Approach and landing fuel flow [kg/min]
        """
        return np.where(self.__engine_type != EngineType.PISTON,
                        # Non piston
                        np.maximum(self.__cal_nominal_fuel_flow(
                            V_tas, Thr), self.__cal_minimum_fuel_flow(H_p)),  # Equation 3.9-5
                        # Piston
                        self.__cal_minimum_fuel_flow(H_p))                                                          # Equation 3.9-8

    def __cal_cruise_fuel_flow(self, V_tas, Thr):
        """
        Calculate fuel flow for cruise (equations 3.9-6 and 3.9-9)

        Parameters
        ----------
        V_tas: float[]
            True airspeed [kt] TODO: Different unit

        Thr: float[]
            Thrust acting parallel to the aircraft velocity vector [N]

        Returns
        -------
        f_cr: float[]
            Cruise fuel flow [kg/min]
        """
        return np.select([self.__engine_type == EngineType.JET,
                          self.__engine_type == EngineType.TURBOPROP,
                          self.__engine_type == EngineType.PISTON],

                         [self.__c_f1 * (1.0 + V_tas/self.__c_f2) * Thr * self.__c_fcr,                     # Equation 3.9-6
                          # Equation 3.9-6
                          self.__c_f1 * (1.0 - V_tas/self.__c_f2) * \
                          (V_tas/1000.0) * Thr * self.__c_fcr,
                          self.__c_f1 * self.__c_fcr])                                                      # Equation 3.9-9

    # ----------------------------  Airline Procedure Models section 4 -----------------------------------------

    def init_procedure_speed(self, m, n):
        """
        Initialize standard air speed schedule for all flight phases (Section 4.1-4.3)

        Parameters
        ----------
        m: float[]
            Aircraft mass [kg]

        n: int
            Index of performance array.
        """
        # Actual stall speed for takeoff
        v_stall_to_act = Unit.mps2kts(self.__cal_operating_speed(
            m, Unit.kts2mps(self.__v_stall_to))[n])
        # Standard climb schedule
        if (self.__engine_type[n] == EngineType.JET):
            # If Jet (Equation 4.1-1~5)
            self.climb_schedule[n] = [self.__C_V_MIN * v_stall_to_act + self.__V_D_CL_1, self.__C_V_MIN * v_stall_to_act + self.__V_D_CL_2, self.__C_V_MIN * v_stall_to_act + self.__V_D_CL_3,
                                      self.__C_V_MIN * v_stall_to_act + self.__V_D_CL_4, self.__C_V_MIN * v_stall_to_act + self.__V_D_CL_5, np.minimum(self.__v_cl_1[n], 250), self.__v_cl_2[n], self.__m_cl[n]]
        else:
            # Else if turboprop and piston (Equation 4.1-6~8)
            self.climb_schedule[n] = [self.__C_V_MIN * v_stall_to_act + self.__V_D_CL_6, self.__C_V_MIN * v_stall_to_act + self.__V_D_CL_7, self.__C_V_MIN * v_stall_to_act + self.__V_D_CL_8,
                                      np.minimum(self.__v_cl_1[n], 250), self.__v_cl_2[n], self.__m_cl[n], 0.0, 0.0]

        # Standard cruise schedule
        if (self.__engine_type[n] == EngineType.JET):
            # If Jet
            self.cruise_schedule[n] = [np.minimum(self.__v_cr_1[n], 170), np.minimum(
                self.__v_cr_1[n], 220), np.minimum(self.__v_cr_1[n], 250), self.__v_cr_2[n], self.__m_cr[n]]
        else:
            # Else if turboprop and piston
            self.cruise_schedule[n] = [np.minimum(self.__v_cr_1[n], 150), np.minimum(
                self.__v_cr_1[n], 180), np.minimum(self.__v_cr_1[n], 250), self.__v_cr_2[n], self.__m_cr[n]]

        # Actual stall speed for landing TODO: consider fuel mass?
        v_stall_ld_act = Unit.mps2kts(self.__cal_operating_speed(
            m, Unit.kts2mps(self.__v_stall_ld))[n])
        # Standard descent schedule
        if (self.__engine_type[n] != EngineType.PISTON):
            # If Jet and Turboprop (Equation 4.3-1~4)
            self.descent_schedule[n] = [self.__C_V_MIN * v_stall_ld_act + self.__V_D_DSE_1, self.__C_V_MIN * v_stall_ld_act + self.__V_D_DSE_2, self.__C_V_MIN * v_stall_ld_act + self.__V_D_DSE_3,
                                        self.__C_V_MIN * v_stall_ld_act + self.__V_D_DSE_4, np.minimum(self.__v_des_1[n], 220), np.minimum(self.__v_des_1[n], 250), self.__v_des_2[n], self.__m_des[n]]
        else:
            # Else if Piston (Equation 4.3-5~7)
            self.descent_schedule[n] = [self.__C_V_MIN * v_stall_ld_act + self.__V_D_DSE_5, self.__C_V_MIN * v_stall_ld_act + self.__V_D_DSE_6, self.__C_V_MIN * v_stall_ld_act + self.__V_D_DSE_7,
                                        self.__v_des_1[n], self.__v_des_2[n], self.__m_des[n], 0.0, 0.0]

    def get_procedure_speed(self, H_p, H_p_trans, flight_phase):
        """
        Get the standard air speed schedule

        Parameters
        ----------
        H_p: float[]
            Geopotential pressuer altitude [ft]

        H_p_trans: float[]
            Transition altitude [ft]

        m: float[]
            Aircraft mass [kg]

        flight_phase: float[]
            Flight phase from Traffic class [Flight_phase enum]

        Returns
        -------
        v_std: float[]
            Standard CAS [kt]
        -or-
        M_std: float[]
            Standard Mach [dimensionless] 

        Notes
        -----
        TODO: Recommended to determine the speed schedule from the highest altitude to the lowest one, 
        and to use at each step the speed of the higher altitude range as a ceiling value for the lower altitude range.

        TODO: Bound the speed schedule form the minimum and maximum speed.
        """
        return np.select([
            flight_phase <= FlightPhase.CLIMB,
            flight_phase == FlightPhase.CRUISE,
            flight_phase >= FlightPhase.DESCENT
        ], [
            # If climb
            np.where(self.__engine_type == EngineType.JET,
                     # If jet
                     np.select([(H_p < 1500), (H_p >= 1500) & (H_p < 3000), (H_p >= 3000) & (H_p < 4000), (H_p >= 4000) & (H_p < 5000), (H_p >= 5000) & (H_p < 6000), (H_p >= 6000) & (H_p < 10000), (H_p >= 10000) & (H_p < H_p_trans), (H_p >= H_p_trans)],
                               [self.climb_schedule[:, 0], self.climb_schedule[:, 1], self.climb_schedule[:, 2], self.climb_schedule[:, 3], self.climb_schedule[:, 4], self.climb_schedule[:, 5], self.climb_schedule[:, 6], self.climb_schedule[:, 7]]),
                     # If turboprop and piston
                     np.select([(H_p < 500), (H_p >= 500) & (H_p < 1000), (H_p >= 1000) & (H_p < 1500), (H_p >= 1500) & (H_p < 10000), (H_p >= 10000) & (H_p < H_p_trans), (H_p >= H_p_trans)],
                               [self.climb_schedule[:, 0], self.climb_schedule[:, 1], self.climb_schedule[:, 2], self.climb_schedule[:, 3], self.climb_schedule[:, 4], self.climb_schedule[:, 5]])
                     ),
            # If cruise
            np.where(self.__engine_type == EngineType.JET,
                     # If jet
                     np.select([(H_p < 3000), (H_p >= 3000) & (H_p < 6000), (H_p >= 6000) & (H_p < 14000), (H_p >= 14000) & (H_p < H_p_trans), (H_p >= H_p_trans)],
                               [self.cruise_schedule[:, 0], self.cruise_schedule[:, 1], self.cruise_schedule[:, 2], self.cruise_schedule[:, 3], self.cruise_schedule[:, 4]]),
                     # If turboprop and piston
                     np.select([(H_p < 3000), (H_p >= 3000) & (H_p < 6000), (H_p >= 6000) & (H_p < 10000), (H_p >= 10000) & (H_p < H_p_trans), (H_p >= H_p_trans)],
                               [self.cruise_schedule[:, 0], self.cruise_schedule[:, 1], self.cruise_schedule[:, 2], self.cruise_schedule[:, 3], self.cruise_schedule[:, 4]])
                     ),
            # If descent
            np.where(self.__engine_type != EngineType.PISTON,
                     # If jet and turboprop
                     np.select([(H_p < 999), (H_p >= 1000) & (H_p < 1500), (H_p >= 1500) & (H_p < 2000), (H_p >= 2000) & (H_p < 3000), (H_p >= 3000) & (H_p < 6000), (H_p >= 6000) & (H_p < 10000), (H_p >= 10000) & (H_p < H_p_trans), (H_p >= H_p_trans)],
                               [self.descent_schedule[:, 0], self.descent_schedule[:, 1], self.descent_schedule[:, 2], self.descent_schedule[:, 3], self.descent_schedule[:, 4], self.descent_schedule[:, 5], self.descent_schedule[:, 6], self.descent_schedule[:, 7]]),
                     # If piston
                     np.select([(H_p < 500), (H_p >= 500) & (H_p < 1000), (H_p >= 1000) & (H_p < 1500), (H_p >= 1500) & (H_p < 10000), (H_p >= 10000) & (H_p < H_p_trans), (H_p >= H_p_trans)],
                               [self.descent_schedule[:, 0], self.descent_schedule[:, 1], self.descent_schedule[:, 2], self.descent_schedule[:, 3], self.descent_schedule[:, 4], self.descent_schedule[:, 5]])
                     )
        ])

    def update_configuration(self, V_cas, H_p, vertical_mode):
        """
        Update configuration (section 3.5)

        V_cas: float[]
            True air speed [knots]

        H_p: float[]
            Geopotential pressuer altitude [ft]

        vertical_mode : float[]
            Vertical mode from Traffic class [Vertical_mode enum]

        Returns
        -------
        configuration : float[]
            configuration from Traffic class [configuration enum]

        TODO: Make use of Airport Elevation in calculation
        """
        return np.select(condlist=[
            (vertical_mode == VerticalMode.CLIMB) & (H_p <= self.__H_MAX_TO),
            (vertical_mode == VerticalMode.CLIMB) & (
                H_p > self.__H_MAX_TO) & (H_p < self.__H_MAX_IC),
            (H_p > self.__H_MAX_IC) | (vertical_mode == VerticalMode.DESCENT) & (
                (V_cas >= (self.__C_V_MIN * self.__v_stall_cr + 10.0))),
            (vertical_mode == VerticalMode.DESCENT) & ((V_cas < self.__C_V_MIN * self.__v_stall_cr + 10.0) & (H_p > self.__H_MAX_LD) & (H_p <= self.__H_MAX_AP)
                                                       ) | ((V_cas < (self.__C_V_MIN * self.__v_stall_cr + 10.0)) & (V_cas >= (self.__C_V_MIN * self.__v_stall_ap + 10.0)) & (H_p <= self.__H_MAX_LD)),
            (vertical_mode == VerticalMode.DESCENT) & (H_p < self.__H_MAX_LD) & (
                V_cas < (self.__C_V_MIN * self.__v_stall_ap + 10.0))
        ],
            choicelist=[
            Config.TAKEOFF,
            Config.INITIAL_CLIMB,
            Config.CLEAN,
            Config.APPROACH,
            Config.LANDING
        ],
            default=Config.CLEAN)

    # ----------------------------  Global aircraft parameters section 5 -----------------------------------------
    def cal_max_d_tas(self, d_t):
        """
        Calculate maximum delta true air speed (equation 5.2-1)

        Parameters
        ----------
        d_t: float[]
            Timestep [s]

        Returns
        -------
        d_v: float[]
            Max delta velocity for time step [ft/s^2]
        """
        return self.__A_L_MAX_CIV * d_t

    def cal_max_d_rocd(self, d_t, V_tas, rocd):
        """
        Calculate maximum delta rate of climb or descend (equation 5.2-2)

        Parameters
        ----------
        d_t: float[]
            Timestep [s]

        V_tas: float[]
            True air speed [ft/s]

        rocd: float[]
            Current rate of climb/descend [ft/s]

        Returns
        -------
        d_rocd: float[]
            Delta rate of climb or descent [ft/s^2]
        """
        return np.sin(np.arcsin(rocd/V_tas) - self.__A_N_MAX_CIV * d_t / V_tas) * (V_tas+d_t)

    def cal_expedite_descend_factor(self, expedite_descent):
        """
        Calculate expedited descent factor for drag multiplication. (Equation 5.4-1)

        Parameters
        ----------
        expedite_descent: bool[]
            Autopilot setting of whether expedite descent is activated

        Returns
        -------
        c_des_exp: float[]
            Coefficient of expedited descent factor [dimensionless]
        """
        return np.where(expedite_descent, self.__C_DES_EXP, 1.0)
