import random
from datetime import datetime, timedelta

start_date = datetime(2026, 1, 1, 0, 0)

total_days = 180   # about 6 months
events_per_day = 120   # camera checks every ~12 minutes

events = []

for day in range(total_days):

    current_day = start_date + timedelta(days=day)

    for i in range(events_per_day):

        time = current_day + timedelta(minutes=i * 12)

        hour = time.hour

        # realistic activity patterns
        if 6 <= hour < 17:
            event = random.choices(
                ["empty", "animal", "human"],
                [0.85, 0.12, 0.03]
            )[0]

        elif 17 <= hour < 21:
            event = random.choices(
                ["animal", "empty", "human"],
                [0.65, 0.30, 0.05]
            )[0]

        elif 21 <= hour < 1:
            event = random.choices(
                ["animal", "human", "empty"],
                [0.55, 0.25, 0.20]
            )[0]

        else:
            event = random.choices(
                ["empty", "animal"],
                [0.90, 0.10]
            )[0]

        # rare fire events
        if random.random() < 0.002:
            event = "fire"

        confidence = round(random.uniform(0.65, 0.96), 2)

        events.append(f"{time} {event} {confidence}")

with open("logs/events.txt", "w") as f:
    for e in events:
        f.write(e + "\n")

print("6 months of realistic forest monitoring logs generated.")
print("Total events:", len(events))