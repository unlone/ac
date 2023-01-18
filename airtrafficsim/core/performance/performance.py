"""Performance base class"""
import numpy as np
from openap import prop, Thrust, Drag, FuelFlow, WRAP

from airtrafficsim.core.performance.bada import Bada
from airtrafficsim.utils.enums import APSpeedMode, Config, VerticalMode
from airtrafficsim.utils.unit_conversion import Unit


class Performance:
    """
    Performance base class
    """

    def __init__(self, performance_mode):
        """
        Initialize Performance base class

        Parameters
        ----------
        N : int, optional
            Number of aircrafts. Maximum size of performance array (pre-initialize to eliminate inefficient append)
            TODO: Revise the initial estimate, by default 1000
        Bada : bool, optional
            Whether to use BADA Performance model, by default False
        """

        self.performance_mode = performance_mode
        """Whether BADA performance model is used [Boolean]"""

        if (self.performance_mode == "BADA"):
            self.perf_model = Bada()
        else:
            # OpenAP
            self.prop_model = []
            self.thrust_model = []
            self.drag_model = []
            self.fuel_flow_model = []
            self.wrap_model = []

            # self.prop_model = np.empty([N], dtype=np.void)
            # self.thrust_model = np.empty([N], dtype=np.void)
            # self.drag_model = np.empty([N], dtype=np.void)
            # self.fuel_flow_model = np.empty([N], dtype=np.void)
            # self.wrap_model = np.empty([N], dtype=np.void)

        self.drag = np.zeros([0])
        """Drag [N]"""
        self.thrust = np.zeros([0])
        """Thrust [N]"""
        self.esf = np.zeros([0])
        """Energy share factor [dimensionless]"""

        # ----------------------------  Atmosphere model (Ref: BADA user menu section 3.1) -----------------------------------------
        # MSL Standard atmosphere condition
        self.__T_0 = 288.15
        """Standard atmospheric temperature at MSL [K]"""
        self.__P_0 = 101325
        """Standard atmospheric pressure at MSL [Pa]"""
        self.__RHO_0 = 1.225
        """Standard atmospheric density at MSL [kg/m^3]"""
        self.__A_0 = 340.294
        """Speed of sound [m/s]"""
        # Expression
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

    def add_aircraft(self, icao, engine=None, mass_class=2):
        """
        Add an aircraft to traffic array.

        Returns
        -------
        n: int
            Index of the added aircraft
        """
        self.drag = np.append(self.drag, 0.0)
        self.thrust = np.append(self.thrust, 0.0)
        self.esf = np.append(self.esf, 0.0)

        if (self.performance_mode == "BADA"):
            self.perf_model.add_aircraft(icao, mass_class)
        else:
            self.prop_model.append(prop.aircraft(icao))
            self.thrust_model.append(Thrust(ac=icao, eng=engine))
            self.drag_model.append(Drag(ac=icao))
            self.fuel_flow_model.append(FuelFlow(ac=icao, eng=engine))
            self.wrap_model.append(WRAP(ac=icao))

    def del_aircraft(self, index):
        """
        Delete an aircraft from traffic array.
        """
        self.drag = np.delete(self.drag, index)
        self.thrust = np.delete(self.thrust, index)
        self.esf = np.delete(self.esf, index)
        if (self.performance_mode == "BADA"):
            self.perf_model.del_aircraft(index)
        else:
            del self.prop_model[index]
            del self.thrust_model[index]
            del self.drag_model[index]
            del self.fuel_flow_model[index]
            del self.wrap_model[index]

    def init_procedure_speed(self, mass, n):
        """
        Initialize standard air speed schedule for all flight phases (Section 4.1-4.3)

        Parameters
        ----------
        m: float[]
            Aircraft mass [kg]

        n: int
            Index of performance array.
        """
        if (self.performance_mode == "BADA"):
            self.perf_model.init_procedure_speed(mass, n)

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
        """
        if (self.performance_mode == "BADA"):
            return self.perf_model.get_procedure_speed(H_p, H_p_trans, flight_phase)
        else:
            return np.array([0])

    # ----------------------------  Atmosphere model (Ref: BADA user menu section 3.1) -----------------------------------------

    def cal_temperature(self, H_p, d_T):
        """
        Calculate Temperature (Equation 3.1-12~16)

        Parameters
        ----------
        H\_p: float[]
            Geopotential pressuer altitude [m]

        d\_T: float[]
            Temperature differential at MSL [K]

        Returns
        -------
        T\_< if below tropopause: float[]
            Temperature [K]

        T\_trop or T\_> if equal to or above tropopause: float[]
            Temperature [K]
        """
        return np.where(H_p < self.__H_P_TROP,
                        # If below Geopotential pressure altitude of tropopause
                        self.__T_0 + d_T + self.__BETA_T_BELOW_TROP * H_p,
                        # If equal or above Geopotential pressure altitude of tropopause
                        self.__T_0 + d_T + self.__BETA_T_BELOW_TROP * self.__H_P_TROP)

    def cal_air_pressure(self, H_p, T, d_T):
        """
        Calculate Air Pressure (Equation 3.1-17~20)

        Parameters
        ----------
        H\_p: float[]
            Geopotential pressuer altitude [m]

        T: float[]
            Temperature from cal_temperature()[K]

        d\_T: float[]
            Temperature differential at MSL [K]

        Returns
        -------
        p\_< or p\_trop if below or equal to tropopause: float[]
            Pressure [Pa]

        p\_> if above tropopause: float[]
            Pressure [Pa]
        """
        return np.where(H_p <= self.__H_P_TROP,
                        # If below or equal Geopotential pressure altitude of tropopause (Equation 3.1-18)
                        self.__P_0 * \
                        np.power((T - d_T) / self.__T_0, -self.__G_0 / \
                                 (self.__BETA_T_BELOW_TROP * self.__R)),
                        # If above Geopotential pressure altitude of tropopause (Equation 3.1-20)
                        self.__P_0 * np.power((self.cal_temperature(self.__H_P_TROP, d_T) - d_T) / self.__T_0, -self.__G_0/(self.__BETA_T_BELOW_TROP * self.__R)) \
                        * np.exp(-self.__G_0/(self.__R * self.cal_temperature(self.__H_P_TROP, 0.0)) * (H_p - self.__H_P_TROP))
                        )

    def cal_air_density(self, p, T):
        """
        Calculate Air Density (Equation 3.1-21)

        Parameters
        ----------
        p: float[]
            Pressure [Pa]

        T: float[]
            Temperature [K]

        Returns
        -------
        rho: float[]
            Density [kg/m^3]
        """
        return p / (self.__R * T)

    def cal_speed_of_sound(self, T):
        """
        Calculate speed of sound. (Equation 3.1-22)

        Parameters
        ----------
        T: float[]
            Temperature [K]

        Returns
        -------
        a: float[]
            Speed of sound [m/s]
        """
        return np.sqrt(self.__KAPPA * self.__R * T)

    def cas_to_tas(self, V_cas, p, rho):
        """
        Convert Calibrated air speed to True air speed. (Equation 3.1-23)

        Parameters
        ----------
        V_cas: float[]
            Calibrated air speed [m/s]

        p: float[]
            Pressure [Pa] 

        rho: float[]
            Density [kg/m^3]

        Returns
        -------
        V_tas : float[]
            True air speed [m/s]
        """
        mu = (self.__KAPPA - 1) / self.__KAPPA
        return np.power(2.0/mu * p/rho * (np.power(1.0 + self.__P_0/p * (np.power(1.0 + mu/2.0 * self.__RHO_0/self.__P_0 * np.square(V_cas), 1.0/mu) - 1), mu)-1), 0.5)

    def tas_to_cas(self, V_tas, p, rho):
        """
        Convert True air speed to Calibrated air speed. (Equation 3.1-24)

        Parameters
        ----------
        V_tas: float[]
            True air speed [m/s]

        p: float[]
            Pressure [Pa] 

        rho: float[]
            Density [kg/m^3]

        Returns
        -------
        V_cas : float[]
            Calibrated air speed [m/s]
        """
        mu = (self.__KAPPA - 1) / self.__KAPPA
        return np.power(2/mu * self.__P_0/self.__RHO_0 * (np.power(1.0 + p/self.__P_0 * (np.power(1 + mu/2 * rho/p * np.square(V_tas), 1.0/mu) - 1.0), mu) - 1.0), 0.5)

    def mach_to_tas(self, M, T):
        """
        Convert Mach number to True Air speed (Equation 3.1-26)

        Parameters
        ----------
        M: float[]
            Mach number [dimensionless]

        T: float[]
            Temperature [K]

        Returns
        -------
        V_tas: float[]
            True air speed [m/s]
        """
        return M * np.sqrt(self.__KAPPA * self.__R * T)

    def tas_to_mach(self, V_tas, T):
        """
        Convert True Air speed to Mach number (Equation 3.1-26)

        Parameters
        ----------
        V_tas: float[]
            True air speed [m/s]

        T: float[]
            Temperature [K]

        Returns
        -------
        M: float[]
            Mach number [dimensionless]
        """
        return V_tas / np.sqrt(self.__KAPPA * self.__R * T)

    # ----------------------------  Operation limit -----------------------------------------
    def cal_transition_alt(self, n, d_T):
        """
        Calculate Mach/CAS transition altitude. (Equation 3.1-27~28)

        Parameters
        ----------
        V_cas: float[]
            Calibrated air speed [m/s]

        M: float[]
            Mach number [dimensionless]

        d_T: float[]
            Temperature differential at MSL [K]

        Returns
        -------
        H_p_trans: float[]
            Transition altitude [m]

        Note
        ----
        Transition altitude is defined to be the geopotential pressure altitude at which V_CAS and M represent the same TAS value.
        TODO: Separate climb and descent trans altitude?
        """
        if (self.performance_mode == "BADA"):
            V_cas = Unit.kts2mps(self.perf_model.climb_schedule[n, -2])
            M = self.perf_model.climb_schedule[n, -1]

            p_trans = self.__P_0 * (np.power(1.0 + (self.__KAPPA-1.0)/2.0 * np.square(V_cas/self.__A_0), self.__KAPPA/(self.__KAPPA-1.0)) - 1.0) \
                / (np.power(1.0 + (self.__KAPPA-1.0)/2.0 * np.square(M), self.__KAPPA/(self.__KAPPA-1.0)) - 1.0)  # Equation 3.1-28
            p_trop = self.cal_air_pressure(
                self.__H_P_TROP, self.cal_temperature(self.__H_P_TROP, d_T), d_T)

            return np.where(p_trans >= p_trop,
                            # If __p_trans >= __p_trop
                            self.__T_0/self.__BETA_T_BELOW_TROP * \
                            (np.power(p_trans/self.__P_0, - \
                             self.__BETA_T_BELOW_TROP*self.__R/self.__G_0) - 1.0),
                            # __p_trans < __p_trop
                            self.__H_P_TROP - self.__R*self.cal_temperature(self.__H_P_TROP, 0.0)/self.__G_0 * np.log(p_trans/p_trop))

        else:
            return np.array([x.climb_cross_alt_conmach()['default'] for x in self.wrap_model])

    def get_empty_weight(self, n):
        """
        Get Empty Weight of an aircraft

        Parameters
        ----------
        n: int
            index of aircraft

        Returns
        -------
        Weight: float
            Empty weight(BADA) or Operating empty weight(OpenAP) [kg]
        """
        if (self.performance_mode == "BADA"):
            return self.perf_model.m_min[n] * 1000.0
        else:
            return self.prop_model[n]['limits']['OEW']

    def cal_maximum_alt(self, d_T, m):
        """
        Calculate maximum altitude

        Parameters
        ----------
        d_T: float[]
            Temperature differential from ISA [K]

        m: float[]
            Aircraft mass [kg]

        Returns
        -------
        h_max: float[]
            Maximum altitude for any given mass [ft]
        """
        if (self.performance_mode == "BADA"):
            return self.perf_model.cal_maximum_altitude(d_T, m)
        else:
            return Unit.m2ft(np.array([x['limits']['ceiling'] for x in self.prop_model]))

    def cal_maximum_speed(self):
        """
        Calculate maximum altitude

        Returns
        -------
        speed, mach: float[]
            Maximum speed and mach
        """
        if (self.performance_mode == "BADA"):
            return self.perf_model.v_mo, self.perf_model.m_mo

    def cal_minimum_speed(self, configuration):
        """
        Calculate minimum speed

        Parameters
        ----------
        configuration: float[]
            configuration from Traffic class [configuration enum]

        Returns
        -------
        v_min: float[]
            Minimum at speed at specific configuration [knots]
        """
        if (self.performance_mode == "BADA"):
            return self.perf_model.cal_minimum_speed(configuration)
        else:
            return 0.0  # TODO: OpenAP no minimum/stall speed?

    def cal_max_d_tas(self, d_t):
        """
        Calculate maximum delta true air speed

        Parameters
        ----------
        d_t: float[]
            Timestep [s]

        Returns
        -------
        d_v: float[]
            Max delta velocity for time step [ft/s^2]
        """
        if (self.performance_mode == "BADA"):
            return self.perf_model.cal_max_d_tas(d_t)
        else:
            return 2 * d_t

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
        if (self.performance_mode == "BADA"):
            return self.perf_model.cal_max_d_rocd(d_t, V_tas, rocd)
        else:
            return np.sin(np.arcsin(rocd/V_tas) - 5.0 * d_t / V_tas) * (V_tas+d_t)

    # ----------------------------  Performance -----------------------------------------
    # ----------------------------  Total-Energy Model Section 3.2 -----------------------------------------

    def cal_energy_share_factor(self, H_p, T, d_T, M, ap_speed_mode, vertical_mode):
        """
        Calculate energy share factor (Equation 3.2-5, 8~11)

        Parameters
        ----------
        H_p: float[]
            Geopotential pressuer altitude [m]

        T: float[]
            Temperature [K]

        d_T: float[]
            Temperature differential at MSL [K]

        M: float[]
            Mach number [dimensionless]

        ap_speed_mode: float[]
            Speed mode from Autopilot class [AP_speed_mode enum]

        vertical_mode: float[]
            Vertical mode from Traffic class [Vertical_mode enum]

        Returns
        -------
        f{M}: float[]
            Energy share factor [dimenesionless]
        """
        return np.select(condlist=[
            ap_speed_mode == APSpeedMode.CONSTANT_MACH,
            ap_speed_mode == APSpeedMode.CONSTANT_CAS,
            ap_speed_mode == APSpeedMode.ACCELERATE,
            ap_speed_mode == APSpeedMode.DECELERATE],

            choicelist=[
            # Constant Mach
            np.where(H_p > self.__H_P_TROP,
                     # Conditiona a: Constant Mach number in stratosphere (Equation 3.2-8)
                     1.0,
                     # Condition b: Constant Mach number below tropopause (Equation 3.2-9)
                     np.power(1.0 + self.__KAPPA*self.__R*self.__BETA_T_BELOW_TROP/2.0/self.__G_0 * np.square(M) * (T-d_T)/T, -1.0)),

            # Constnt CAS
            np.where(H_p <= self.__H_P_TROP,
                     # Condition c: Constant Calibrated Airspeed (CAS) below tropopause (Equation 3.2-10)
                     np.power(1.0 + self.__KAPPA*self.__R*self.__BETA_T_BELOW_TROP/2.0/self.__G_0 * np.square(M) * (T-d_T)/T \
                              + np.power(1.0 + (self.__KAPPA-1.0)/2.0 * np.square(M), -1.0/(self.__KAPPA-1.0)) \
                              * (np.power(1.0 + (self.__KAPPA-1.0)/2.0 * np.square(M), self.__KAPPA/(self.__KAPPA-1.0)) - 1.0), -1.0),
                     # Condition d: Constant Calibrated Airspeed (CAS) above tropopause (Equation 3.2-11)
                     np.power(1.0 + np.power(1.0 + (self.__KAPPA-1.0)/2.0 * np.square(M), -1.0/(self.__KAPPA-1)) \
                              * (np.power(1.0 + (self.__KAPPA-1.0)/2.0 * np.square(M), self.__KAPPA/(self.__KAPPA-1.0)) - 1.0), -1.0)),

            # Acceleration in climb + Acceleration in descent
            (vertical_mode == VerticalMode.CLIMB) * 0.3 + \
            (vertical_mode == VerticalMode.DESCENT) * 1.7,

            # Deceleration in descent + Deceleration in climb
            (vertical_mode == VerticalMode.DESCENT) * 0.3 + \
            (vertical_mode == VerticalMode.CLIMB) * 1.7
        ])

    def cal_tem_rocd(self, T, d_T, m, D, f_M, Thr, V_tas, C_pow_red):
        """
        Total Energy Model. Speed and Throttle Controller. (BADA User Menu Equation 3.2-1a and 3.2-7)
        Calculate Rate of climb or descent given velocity(constant) and thrust (max climb thrust/idle descent).

        Parameters
        ----------
        T: float[]
            Temperature [K]

        d_T: float[]
            Temperature differential at MSL [K]

        m: float[]
            Aircraft mass [kg]

        D: float[]
            Aerodynamic drag [N]

        f{M}: float[]
            Energy share factor [dimenesionless]

        Thr: float[]
            Thrust acting parallel to the aircraft velocity vector [N]

        V_tas: float[]
            True airspeed [m/s]

        C_pow_red: float[]
            Reduced climb power coefficient [dimensionless]

        Returns
        -------
        rocd: float[]
            Rate of climb or descent [m/s]
            Defined as variation with time of the aircraft geopotential pressure altitude H_p
        """
        return (T-d_T)/T * (Thr-D)*V_tas*C_pow_red/m/self.__G_0 * f_M

    def cal_tem_accel(self, T, d_T, m, D, rocd, Thr, V_tas):
        """
        Total Energy Model. ROCD and Throttle Controller. (BADA User Menu Equation 3.2-1b and 3.2-7) NOTE: changed to equation  3.2-1
        Calculate accel given ROCD and thrust.

        Parameters
        ----------
        T: float[]
            Temperature [K]

        d_T: float[]
            Temperature differential at MSL [K]

        m: float[]
            Aircraft mass [kg]

        D: float[]
            Aerodynamic drag [N]    

        rocd: float[]
            Rate of climb or descent [m/s]

        Thr: float[]
            Thrust acting parallel to the aircraft velocity vector [N]

        V_tas: float[]
            True airspeed [m/s]

        Returns
        -------
        accel: float[]
            Acceleration of tur air speed [m/s^2]
        """
        # return rocd / f_M / ((T-d_T)/T) * m*self.__G_0 / (Thr-D)
        return np.where(V_tas == 0, (Thr - D) / m, (Thr - D) / m - self.__G_0 / V_tas * rocd*T/(T-d_T))

    def cal_tem_thrust(self, T, d_T, m, D, f_M, rocd, V_tas):
        """
        Total Energy Model. Speed and ROCD Controller. (BADA User Menu Equation 3.2-1c and 3.2-7) TODO: change to equation  3.2-1
        Calculate thrust given ROCD and speed.

        Parameters
        ----------
        T: float[]
            Temperature [K]

        d_T: float[]
            Temperature differential at MSL [K]

        D: float[]
            Aerodynamic drag [N]

        m: float[]
            Aircraft mass [kg]

        f{M}: float[]
            Energy share factor [dimenesionless]

        rocd: float[]
            Rate of climb or descent [m/s]

        V_tas: float[]
            True airspeed [m/s]

        Returns
        -------
        Thr: float[]
            Thrust acting parallel to the aircraft velocity vector [N]
        """
        return rocd / f_M / ((T-d_T)/T) * m*self.__G_0 / V_tas + D

    def cal_vs_accel(self, traffic, tas):
        if (self.performance_mode == "BADA"):
            # Drag and Thrust
            self.drag = self.perf_model.cal_aerodynamic_drag(tas, traffic.bank_angle, traffic.mass, traffic.weather.rho,
                                                             traffic.configuration, self.perf_model.cal_expedite_descend_factor(traffic.ap.expedite_descent))
            self.thrust = self.perf_model.cal_thrust(
                traffic.vertical_mode, traffic.configuration, traffic.alt, traffic.tas, traffic.weather.d_T, self.drag, traffic.ap.speed_mode)
        else:
            self.drag = np.array([x.clean(mass=traffic.mass, tas=traffic.tas,
                                 alt=traffic.alt, path_angle=traffic.path_angle) for x in self.drag_model])
            # drag.nonclean(mass=60000, tas=150, alt=100, flap_angle=20, path_angle=10, landing_gear=True)
            self.thrust = np.array(
                [x.cruise(tas=traffic.cas, alt=traffic.alt) for x in self.thrust_model])
            # T = thrust.takeoff(tas=100, alt=0) T = thrust.climb(tas=200, alt=20000, roc=1000)

        # Total Energy Model
        self.esf = self.cal_energy_share_factor(Unit.ft2m(traffic.alt), traffic.weather.T, traffic.weather.d_T,
                                                traffic.mach, traffic.ap.speed_mode, traffic.vertical_mode)      # Energy share factor
        if (self.performance_mode == "BADA"):
            rocd = self.cal_tem_rocd(traffic.weather.T, traffic.weather.d_T, traffic.mass, self.drag, self.esf,
                                     self.thrust, tas, self.perf_model.cal_reduced_climb_power(traffic.mass, traffic.alt, traffic.max_alt))
        else:
            rocd = self.cal_tem_rocd(traffic.weather.T, traffic.weather.d_T,
                                     traffic.mass, self.drag, self.esf, self.thrust, tas, 1.0)

        accel = np.where((traffic.ap.speed_mode == APSpeedMode.ACCELERATE) | (traffic.ap.speed_mode == APSpeedMode.DECELERATE),
                         self.cal_tem_accel(
                             traffic.weather.T, traffic.weather.d_T, traffic.mass, self.drag, rocd, self.thrust, tas),
                         0.0)

        return Unit.mps2ftpm(rocd), accel

    def cal_fuel_burn(self, flight_phase, tas, alt):
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
        """
        if (self.performance_mode == "BADA"):
            return self.perf_model.cal_fuel_burn(flight_phase, tas, self.thrust, alt)
        else:
            return [x.at_thrust(acthr=self.thrust, alt=alt) for x in self.fuel_flow_model]
        # FF = fuelflow.takeoff(tas=100, alt=0, throttle=1)
        # FF = fuelflow.enroute(mass=60000, tas=200, alt=20000, path_angle=3)
        # FF = fuelflow.enroute(mass=60000, tas=230, alt=32000, path_angle=0)

    # ----------------------------  Turning -----------------------------------------
    def cal_rate_of_turn(self, bank_angle, V_tas):
        """
        Calculate rate of turn (Equation 5.3-1)

        Parameters
        ----------
        bank_angle: float[]
            Bank angle [deg]

        V_tas: float[]
            True air speed [m/s]

        Returns
        -------
        Rate of turn : float[]
            Rate of turn [deg/s]
        """
        return np.rad2deg(self.__G_0 / V_tas * np.tan(np.deg2rad(bank_angle)))

    def cal_bank_angle(self, rate_of_turn, V_tas):
        """
        Calculate rate of turn (Equation 5.3-1)

        Parameters
        ----------
        Rate of turn : float[]
            Rate of turn [deg/s]

        V_tas: float[]
            True air speed [m/s]

        Returns
        -------
        bank_angle: float[]
            Bank angle [deg]
        """
        return np.rad2deg(np.arctan(np.deg2rad(rate_of_turn) * V_tas / self.__G_0))

    def cal_turn_radius(self, bank_angle, V_tas):
        """
        Calculate rate of turn (Equation 5.3-1)

        Parameters
        ----------
        bank_angle: float[]
            Bank angle [deg]

        V_tas: float[]
            True air speed [m/s]

        Returns
        -------
        turn_radius: float[]
            Turn radius [m]
        """
        return np.square(V_tas) / self.__G_0 / np.tan(np.deg2rad(bank_angle))

    def get_bank_angles(self, configuration):
        """
        Get standard nominal bank angles (Session 5.3)

        Parameters
        ----------
        configuration: float[]
            configuration from Traffic class [configuration enum]

        Returns
        -------
        bank_angles :float 
            Bank angles [deg]
        """
        if (self.performance_mode == "BADA"):
            return np.where((configuration == Config.TAKEOFF) | (configuration == Config.LANDING), self.perf_model._Bada__PHI_NORM_CIV_TOLD, self.perf_model._Bada__PHI_NORM_CIV_OTHERS)
        else:
            return np.where((configuration == Config.TAKEOFF) | (configuration == Config.LANDING), 15.0, 30.0)

    def update_configuration(self, V_cas, H_p, vertical_mode):
        """
        Update Flight Phase (section 3.5)

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
        """
        if (self.performance_mode == "BADA"):
            return self.perf_model.update_configuration(V_cas, H_p, vertical_mode)
        else:
            return np.array([Config.CLEAN])
