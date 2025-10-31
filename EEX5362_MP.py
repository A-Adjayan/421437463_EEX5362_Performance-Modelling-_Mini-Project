#421437463
# Performance Modeling of Hospital Triage and Treatment System using SimPy
# Author: [Your Name]
# Course: Performance Modeling Mini Project

import simpy
import random
import statistics
import matplotlib.pyplot as plt

# ----------------------------
# 1. Simulation Parameters
# ----------------------------
RANDOM_SEED = 42
NUM_DOCTORS = 4
SIM_TIME = 12 * 60  # 12 hours (in minutes)

# Patient arrival rate (mean time between arrivals)
INTER_ARRIVAL_TIME = 6  # on average, 1 patient every 6 minutes

# ----------------------------
# 2. Performance Data
# ----------------------------
waiting_times = []
treatment_times = []
system_times = []
triage_levels = []


# ----------------------------
# 3. Triage Level Generator
# ----------------------------
def get_triage_level():
    return random.choices(
        ["Critical", "Urgent", "Non-Urgent"],
        weights=[0.2, 0.5, 0.3]
    )[0]


# ----------------------------
# 4. Service Time Distributions
# ----------------------------
def triage_time(level):
    return random.randint(4, 8)


def treatment_time(level):
    if level == "Critical":
        return random.randint(40, 60)
    elif level == "Urgent":
        return random.randint(25, 45)
    else:
        return random.randint(20, 35)


# ----------------------------
# 5. Patient Process
# ----------------------------
def patient(env, name, doctors):
    """Simulates a single patient's flow through triage and treatment."""
    arrival = env.now
    level = get_triage_level()
    triage_levels.append(level)

    # Triage
    yield env.timeout(triage_time(level))

    # Request doctor (queue if none available)
    with doctors.request() as req:
        yield req
        wait = env.now - arrival
        waiting_times.append(wait)

        # Treatment
        treat_dur = treatment_time(level)
        treatment_times.append(treat_dur)
        yield env.timeout(treat_dur)

        total_time = env.now - arrival
        system_times.append(total_time)


# ----------------------------
# 6. Patient Arrival Generator
# ----------------------------
def patient_generator(env, doctors):
    """Generates patients arriving randomly based on an exponential distribution."""
    i = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / INTER_ARRIVAL_TIME))
        i += 1
        env.process(patient(env, f"Patient {i}", doctors))


# ----------------------------
# 7. Run Simulation
# ----------------------------
print("Starting simulation...")
random.seed(RANDOM_SEED)
env = simpy.Environment()
doctors = simpy.Resource(env, NUM_DOCTORS)
env.process(patient_generator(env, doctors))
env.run(until=SIM_TIME)

# ----------------------------
# 8. Report Results
# ----------------------------
print("\n=== PERFORMANCE RESULTS ===")
print(f"Total Patients Treated: {len(waiting_times)}")
print(f"Average Waiting Time: {statistics.mean(waiting_times):.2f} minutes")
print(f"Average Treatment Duration: {statistics.mean(treatment_times):.2f} minutes")
print(f"Average Total Time in System: {statistics.mean(system_times):.2f} minutes")

# Waiting times per triage level
critical_waits = [w for w, l in zip(waiting_times, triage_levels) if l == "Critical"]
urgent_waits = [w for w, l in zip(waiting_times, triage_levels) if l == "Urgent"]
nonurgent_waits = [w for w, l in zip(waiting_times, triage_levels) if l == "Non-Urgent"]

print("\nAverage Waiting Time by Triage Level:")
print(f"Critical: {statistics.mean(critical_waits):.2f} min")
print(f"Urgent: {statistics.mean(urgent_waits):.2f} min")
print(f"Non-Urgent: {statistics.mean(nonurgent_waits):.2f} min")

# ----------------------------
# 9. Visualization
# ----------------------------
plt.figure(figsize=(8,5))
plt.hist(waiting_times, bins=20, edgecolor='black')
plt.title("Distribution of Patient Waiting Times")
plt.xlabel("Waiting Time (minutes)")
plt.ylabel("Number of Patients")
plt.show()

plt.figure(figsize=(8,5))
plt.boxplot([critical_waits, urgent_waits, nonurgent_waits],
            labels=["Critical", "Urgent", "Non-Urgent"])
plt.title("Waiting Time by Triage Level")
plt.ylabel("Minutes")
plt.show()
