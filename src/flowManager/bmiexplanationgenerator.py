import random


class BMIExplanationGenerator:
    def __init__(self):
        self._extremely_below_average = [
            "You are extremely below the average bmi, make sure you get medical consultation about your diet."
        ]
        self._below_average = [
            "You are below the average bmi, but it is not too late to get your diet back on track. For more information "
            "please contact your family doctor."
        ]
        self._average = [
            "Great work! "
            "You should keep your current life-style",
            "In some areas of life, being an average person is not great, but when it comes to bmi score, it's the best!"
        ]
        self._above_average = [
            "You are above the average bmi, but it is not too late to get your diet back on track. Just remember to keep "
            "an healthy diet and do some exercise.",
            "You should exercise some more and keep an healthy diet."
        ]
        self._extremely_above_average = [
            "You are obese, it can harm your life-quality and you health. Please get medical consultation about your diet.",
            "Obesity can be quite dangerous if not treated. Please get medical consultation about your diet."
        ]

    def generate_explanation(self, bmi_score):
        if bmi_score < 14:
            return self._extremely_below_average[random.randint(0, len(self._extremely_below_average) - 1)]
        elif bmi_score < 18:
            return self._below_average[random.randint(0, len(self._below_average) - 1)]
        elif bmi_score < 25:
            return self._average[random.randint(0, len(self._average) - 1)]
        elif bmi_score < 30:
            return self._above_average[random.randint(0, len(self._above_average) - 1)]
        else:
            return self._extremely_above_average[random.randint(0, len(self._extremely_above_average) - 1)]