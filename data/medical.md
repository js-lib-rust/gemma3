## Medical Agent

This agent assists in the management and archiving of health-related measurements taken at home. It processes user prompts to save new measurement data and retrieve existing records for inspection. To ensure data persistence, it utilizes a database solution that can be deployed either locally (on-premise) or within a cloud environment. 

The Medical Agent supports a wide range of common home health measurements including: body weight, body temperature, blood pressure readings, glucose levels, and oxygen saturation. It is designed to accommodate *all* measurement types for which compatible at-home devices are available.

Beyond simply listing data, the Medical Agent provides advanced analytical capabilities. It can **review measurements over specified time periods**, **discover trends** in health data, and **detect anomalies** that may require attention.  The agent is capable of **creating reports and statistics** based on collected data, and can **send these reports via email** to designated recipients for convenient monitoring and sharing with healthcare professionals.

## Health Measurements

The Medical Agent supports a comprehensive range of health measurement groups, categorized as follows:

*   **Anthropometric Data:** This category encompasses fundamental body measurements crucial for overall health assessment. It includes metrics such as height, weight, body temperature, and Body Mass Index (BMI). These provide baseline indicators of physical status and growth trends.
*   **Cardiovascular Metrics:** Focusing on the circulatory system, this group tracks vital signs related to heart function and arterial health. Examples include blood pressure readings (systolic & diastolic), heart rate (resting & active) and pulse pressure.
*   **Biochemical Data:** This category covers measurements analyzing bodily fluids, primarily blood, to assess internal health conditions. It includes glucose levels and oxygen saturation (SpO2).
*   **Cognitive Assessments:**  This group focuses on monitoring brain health and cognitive performance over time. It encompasses measurements from IQ tests, memory assessments, reaction time evaluations, sleep pattern analysis, etc. These help identify potential changes or declines in cognitive function.

### Anthropometric Data

This category encompasses fundamental body measurements crucial for overall health assessment. Here are the types supported:

*   **Body Height:** The vertical distance from the floor to the top of the head while standing erect on a flat surface. Measured in centimeters (cm).
*   **Body Weight:** The total mass of the body, comprising muscle, bone, fat, water, and organs. Measured in kilograms (kg).
*   **Body Mass Index (BMI):** A screening tool calculated using height and weight to estimate body fat percentage. Represented as a scalar value without units.
*   **Body Temperature:**  A measure of the body's internal heat, indicating health status and metabolic function. Measured in degrees Celsius (°C).

### Cardiovascular Metrics

This group tracks vital signs related to heart function and arterial health. Here are the types supported:

*   **Systolic Pressure:** The higher value in a blood pressure reading, representing the pressure in arteries during ventricular contraction (heartbeat). Measured in millimeters of mercury (mmHg).
*   **Diastolic Pressure:** The lower value in a blood pressure reading, representing the pressure in arteries during ventricular relaxation (between heartbeats). Measured in millimeters of mercury (mmHg).
*   **Pulse Pressure (PP):**  The difference between systolic and diastolic blood pressure values, indicating arterial stiffness. Measured in millimeters of mercury (mmHg).
*   **Heart Rate (Pulse):** The number of times the heart beats per minute (bpm), reflecting cardiac workload. Measured in beats per minute (bpm).

### Biochemical Data

This category covers measurements analyzing bodily fluids, primarily blood, to assess internal health conditions. Here are the types supported:

*   **Glucose Level (Blood Sugar):** Measures the concentration of glucose in the blood, representing the body's primary energy source. Measured in milligrams per deciliter (mg/dL).
*   **Oxygen Saturation Level (SpO2):**  Indicates the percentage of hemoglobin carrying oxygen in the blood, reflecting oxygen transport efficiency. Expressed as a percentage (%).

### Cognitive Assessments

This group focuses on monitoring brain health and cognitive performance over time. It encompasses measurements from standardized tests, assessments of daily function, and increasingly, data from engaging quiz-based activities designed to track changes in specific cognitive domains. Here are the types supported:

*   **Intelligence Quotient (IQ):** A standardized score derived from comprehensive tests assessing a broad range of cognitive abilities such as reasoning, problem-solving, memory, and verbal comprehension. Represented as a scalar value without units.
*   **Sleep Duration:**  A record of the length of sleep intervals, whether nocturnal or diurnal. Measured in hours.
*   **Quiz Game Scores – Verbal Reasoning:** Tracks performance on quizzes testing vocabulary, analogies, sentence completion, and logical deduction. Recorded as a score (e.g., 0-100).
*   **Quiz Game Scores – Spatial Reasoning:**  Tracks performance on quizzes involving mental rotation, pattern recognition, and visual problem-solving. Recorded as a score (e.g., 0-100).
*   **Quiz Game Scores – Memory Recall:** Tracks performance on quizzes testing short-term and long-term memory retention of facts, lists, or sequences. Recorded as a score (e.g., 0-100).
*   **Quiz Game Scores – Reaction Time:** Measures the speed of response to visual or auditory stimuli in interactive games. Recorded in milliseconds (ms).
*   **Quiz Game Scores - Numerical Reasoning:** Tracks performance on quizzes testing mathematical problem solving, data interpretation and logical thinking with numbers. Recorded as a score (e.g., 0-100).

This diverse range of assessments allows for a more nuanced understanding of cognitive function and potential changes over time, providing valuable insights into brain health evolution.

## Health Measurement Structure

The 'health measurement' is represented as a JSON object containing the type of measurement and its corresponding numeric value. Function responses may include one or multiple health measurements, formatted in JSONL (JSON Lines) format. These measurements are persistently stored within the medical database.

It comprises the following properties:

*   **timestamp**: A date string representing when the measurement was taken, adhering to the YYYY-MM-DD HH:MM:SS format.
*   **person**: The name of the individual associated with the measurement; a string value.
*   **measurement**:  The specific type of health measurement recorded; a string value (e.g., "body_height", "glucose_level").
*   **value**: The numeric value representing the measurement result.

Here is an example of a health measurement object:

```json
{
  "timestamp": "2025-12-17 08:47:02",
  "person": "Iulian Rotaru",
  "measurement": "systolic_pressure",
  "value": 124
}
```

## What is blood pressure?
Blood pressure is the force of your blood pushing against your artery walls as your heart pumps it through your body.

## What is normal value for systolic blood pressure?
A normal systolic blood pressure (the top number) for adults is less than 120 mmHg. Readings between 120-129 systolic are considered elevated, while 130 or higher starts to indicate high blood pressure (hypertension).

## What is normal value for diastolic blood pressure?
A normal diastolic blood pressure (the bottom number) for adults is less than 80 mmHg, with the ideal being below 80 mmHg. Readings of 80-89 mmHg indicate elevated or Stage 1 hypertension, requiring attention, while 90 mmHg or higher signifies Stage 2 hypertension.

## What is normal value for pulse pressure?
Pulse pressure (PP) is typically around 40 mmHg in healthy adults. While a normal pulse pressure indicates healthy artery flexibility, a wide (high) or narrow (low) reading can signal underlying issues like stiff arteries or low blood volume.

## What is normal value for heart rate?
A normal resting heart rate for adults is typically between 60 and 100 bpm, but it varies with activity, fitness, age, emotions.

## What is normal value for glucose level?
Normal blood glucose levels are generally below 100 mg/dL when fasting, and below 140 mg/dL two hours after a meal.

## What is normal value for oxygen saturation level?
A normal blood oxygen saturation (SpO2) for a healthy person is 95% to 100%.

## How body mass index is classified?
BMI Categories (Adults)

*   **Underweight**: below 18.5
*   **Normal Weight**: 18.5 – 24.9
*   **Overweight**: 25.0 – 29.9
*   **Obese**: 30.0 or higher

## What is normal range for body temperature?
While 37°C is a classic average for body temperature, a normal range for adults is generally considered 36.1°C to 37.2°C, with fluctuations common.

## What is normal range for IQ?
Average intelligence quotient (IQ) is generally defined as a score between 90 and 109, with the statistical average set at 100. This range encompasses the majority of the population.

## How is body_temperature parameter displayed?
Parameter body_temperature is displayed as 'Body Temperature'. It is measured in Celsius degrees (°C).

## What is the function parameter for 'Body Temperature'?
The function parameter for 'Body Temperature' is body_temperature.

## How is body_weight parameter displayed?
Parameter body_weight is displayed as 'Body Weight'. It is measured in kilograms (kg).

## What is the function parameter for 'Body Weight'?
The function parameter for 'Body Weight' is body_weight.

## How is body_height parameter displayed?
Parameter body_height is displayed as 'Body Height'. It is measured in centimeters (cm).

## What is the function parameter for 'Body Height'?
The function parameter for 'Body Height' is body_height.

## How is body_max_index parameter displayed?
Parameter body_max_index is displayed as 'Body Mass Index (BMI)'. It is a scalar value and has no measurement units.

## What is the function parameter for 'Body Mass Index (BMI)'?
The function parameter for 'Body Mass Index (BMI)' is body_max_index.

## How is systolic_pressure parameter displayed?
Parameter systolic_pressure is displayed as 'Systolic Pressure'. It is a measured in millimeters of mercury (mmHg).

## What is the function parameter for 'Systolic Pressure'?
The function parameter for 'Systolic Pressure' is systolic_pressure.

## How is diastolic_pressure parameter displayed?

Parameter diastolic_pressure is displayed as 'Diastolic Pressure'. It is a measured in millimeters of mercury (mmHg).
## What is the function parameter for 'Diastolic Pressure'?

The function parameter for 'Diastolic Pressure' is diastolic_pressure.
## How is pulse_pressure parameter displayed?

Parameter pulse_pressure is displayed as 'Pulse Pressure'. It is a measured in millimeters of mercury (mmHg).
## What is the function parameter for 'Pulse Pressure'?

The function parameter for 'Pulse Pressure' is pulse_pressure.
## How is heart_rate parameter displayed?

Parameter heart_rate is displayed as 'Heart Rate'. It is a measured in millimeters of mercury (mmHg).
## What is the function parameter for 'Heart Rate'?
The function parameter for 'Heart Rate' is heart_rate.

## How is glucose_level parameter displayed?
Parameter glucose_level is displayed as 'Glucose Level' or 'Blood Sugar'. IT is measured in milligrams per deciliter (mg/dL).

## What is the function parameter for 'Glucose Level'?
The function parameter for 'Glucose Level' is glucose_level.

## What is the function parameter for 'Blood Sugar'?
The function parameter for 'Blood Sugar' is glucose_level.

## How is oxygen_saturation parameter displayed?
Parameter oxygen_saturation is displayed as 'Oxygen Saturation Level (SpO2)'. It is expressed as percent.

## What is the function parameter for 'Oxygen Saturation Level (SpO2)'?
The function parameter for 'Oxygen Saturation Level (SpO2)' is oxygen_saturation.

## What does spo2 stand for?
The acronym spo2 stand for Oxygen Saturation Level. It is a blood related measurement.

## What means spo2?
SpO2 means oxygen saturation, representing the percentage of oxygen-carrying hemoglobin in your blood.

## What is the acronym for Oxygen Saturation Level?
The acronym for Oxygen Saturation Level is SpO2.

## How is intelligence_quotient parameter displayed?
Parameter intelligence_quotient is displayed as 'Intelligence QuotientIndex (IQ)'. It is a scalar value without
measurement units.

## What is the function parameter for 'Intelligence QuotientIndex (IQ)'?
The function parameter for 'Intelligence QuotientIndex (IQ)' is intelligence_quotient.
