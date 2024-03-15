import krpc
import json
import uuid
import elastic 
import nifi
import time

# Track errors globally
errors = {}

def capture():
    # Initialize Elastic
    flight_id = '001' #str(uuid.uuid4()).split('-')[1]
    print(f"Flight ID: {flight_id}")
    storage = elastic.Elastic(f'telemetry-kts-{flight_id}', delete_index=True)
    #storage = nifi.NiFi('http://localhost:8082')

    # Connect to KSP
    conn = krpc.connect(name='KerbalTelemetrySystem')
    vessel = conn.space_center.active_vessel
    sc = SpaceCraft(vessel)

    # Get telemetry at 4Hz
    print('Getting telemetry ...')
    frequency = 4
    last_time = 0
    while 1:
        now = time.time()
        if (now - last_time) > 1/frequency:
            frame = sc.get_telemetry_frame()
            for doc in frame:
                storage.put(doc)
            #print(json.dumps(frame, indent=4))
            last_time = now

def dump(fpath='telemetry-dump.json'):
    print("Not implemented yet.")
    #storage = elastic.Elastic(f'telemetry-kts-001', delete_index=False)
    #data = storage.get_all({})
    #with open(fpath, 'w') as f:
    #    f.write(json.dumps(data, indent=4))


class SpaceCraft:
    def __init__(self, vessel):
        self.vessel = vessel
        self.name = vessel.name
        self.parts = {}
        print(f"Initializing SpaceCraft {self.name} ... ")
        parts = vessel.parts.all
        for part in parts:
            print('    Adding part ... ', part.name, '|', part.title, end=' ... ')
            p = self.add_part(part)
            print('UUID: ', p._id)
        print('SpaceCraft initialized.')
    
    def add_part(self, part):
        _id = str(uuid.uuid4())
        self.parts[_id] = Part(_id, part)
        return self.parts[_id]
    
    def get_telemetry_frame(self):
        frame = []
        for part in self.parts.values():
            data_point = part.get_telemetry_frame()
            if data_point is not None:
                frame.append(data_point)
        data_point = self.get_sc_frame()
        if data_point is not None:
            frame.append(data_point)
        return frame

    def get_sc_frame(self):
        orbit = self.vessel.orbit
        flight = self.vessel.flight(orbit.body.reference_frame)
        frame = {
            'uuid': '__spacecraft__', # 'spacecraft-uuid' is a placeholder for the actual UUID of the spacecraft
            'name': self.name,
            'met': self.vessel.met,
            # Vessel characteristics
            'mass': self.vessel.mass,
            'dry_mass': self.vessel.dry_mass,
            'thrust': self.vessel.thrust,
            'available_thrust': self.vessel.available_thrust,
            'max_thrust': self.vessel.max_thrust,
            'max_vacuum_thrust': self.vessel.max_vacuum_thrust,
            'specific_impulse': self.vessel.specific_impulse,
            'vacuum_specific_impulse': self.vessel.vacuum_specific_impulse,
            'moment_of_inertia': self.vessel.moment_of_inertia,
            'inertia_tensor': self.vessel.inertia_tensor,
            'available_torque': self.vessel.available_torque,
            'available_reaction_wheel_torque': self.vessel.available_reaction_wheel_torque,
            'available_rcs_torque': self.vessel.available_rcs_torque,
            'available_engine_torque': self.vessel.available_engine_torque,
            'available_control_surface_torque': self.vessel.available_control_surface_torque,
            'situation': self.vessel.situation.name,
            # Flight characteristics
            'g_force': flight.g_force,
            'mean_altitude': flight.mean_altitude,
            'surface_altitude': flight.surface_altitude,
            'bedrock_altitude': flight.bedrock_altitude,
            'elevation': flight.elevation,
            'latitude': flight.latitude,
            'longitude': flight.longitude,
            'speed': flight.speed,
            'velocity': flight.velocity,
            'horizontal_speed': flight.horizontal_speed,
            'vertical_speed': flight.vertical_speed,
            'center_of_mass': flight.center_of_mass,
            'rotation': flight.rotation,
            'direction': flight.direction,
            'pitch': flight.pitch,
            'heading': flight.heading,
            'roll': flight.roll,
            'atmosphere_density': flight.atmosphere_density,
            'static_pressure': flight.static_pressure,
            'dynamic_pressure': flight.dynamic_pressure,
            'aerodynamic_force': flight.aerodynamic_force,
            'lift': flight.lift,
            'drag': flight.drag,
            'speed_of_sound': flight.speed_of_sound,
            'mach': flight.mach,
            'true_air_speed': flight.true_air_speed,
            'equivalent_air_speed': flight.equivalent_air_speed,
            'angle_of_attack': flight.angle_of_attack,
            'sideslip_angle': flight.sideslip_angle,
            'total_air_temperature': flight.total_air_temperature,
            'static_air_temperature': flight.static_air_temperature,
            # Orbit characteristics
            'apoapsis': orbit.apoapsis,
            'periapsis': orbit.periapsis,
            'apoapsis_altitude': orbit.apoapsis_altitude,
            'periapsis_altitude': orbit.periapsis_altitude,
            'semi_major_axis': orbit.semi_major_axis,
            'semi_minor_axis': orbit.semi_minor_axis,
            'radius': orbit.radius,
            'orbital_speed': orbit.speed,
            'orbital_period': orbit.period,
            'time_to_apoapsis': orbit.time_to_apoapsis,
            'time_to_periapsis': orbit.time_to_periapsis,
            'eccentricity': orbit.eccentricity,
            'inclination': orbit.inclination,
            'longitude_of_ascending_node': orbit.longitude_of_ascending_node,
            'argument_of_periapsis': orbit.argument_of_periapsis,
            'mean_anomaly_At_epoch': orbit.mean_anomaly_at_epoch,
            'epoch': orbit.epoch,
            'mean_anomaly': orbit.mean_anomaly,
            'true_anomaly': orbit.true_anomaly,
            'eccentric_anomaly': orbit.eccentric_anomaly,
            # Comms characteristics
            'can_communicate': self.vessel.comms.can_communicate,
            'signal_strength': self.vessel.comms.signal_strength,
            'signal_delay': self.vessel.comms.signal_delay,
            'comms_power': self.vessel.comms.power,
        }
        return frame


class Part:

    def __init__(self, part_id, part):
        self._id = part_id
        self._name = part.name
        self._part = part

    def get_telemetry_frame(self):
        if errors.get(self._id, 0) > 3:
            print(f"Skipping part {self._name} ({self._id}) due to too many errors.")
            return None
        try:
            frame = {
                'uuid': self._id,
                'name': self._name,
                'mass': self._part.mass,
                'dry_mass': self._part.dry_mass,
                'dynamic_pressure': self._part.dynamic_pressure,
                'temperature': self._part.temperature,
                'skin_temperature': self._part.skin_temperature,
                'thermal_conduction_flux': self._part.thermal_conduction_flux,
                'thermal_convection_flux': self._part.thermal_convection_flux,
                'thermal_radiation_flux': self._part.thermal_radiation_flux,
                'thermal_internal_flux': self._part.thermal_internal_flux
            }
            for resource in self._part.resources.all:
                frame[f"{resource.name}_amt"] = resource.amount
                frame[f"{resource.name}_max"] = resource.max
            return frame
        except Exception as e:
            print(f"Error getting telemetry frame for part {self._name}")
            if self._id not in errors.keys():
                errors[self._id] = 0
            errors[self._id] += 1
            return None

    

if __name__ == '__main__':
    main()