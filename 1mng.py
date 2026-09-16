from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd

@dataclass
class RiskModel:
    Q: float = 100.0
    P: float = 10.0
    VC: float = 5.0
    FC: float = 300.0
    rD: float = 0.1
    D: float = 500.0
    E: float = 500.0
    tax: float = 0.2
    # Сценарии
    scenarios: List[dict] = field(default_factory=lambda: [
        {"id": 1, "Q": 80.0, "prob": 0.2},
        {"id": 2, "Q": 100.0, "prob": 0.7},
        {"id": 3, "Q": 120.0, "prob": 0.1},
    ])
    @property
    def S(self) :
        return self.Q * self.P
    @property
    def C(self):
        return self.VC * self.Q + self.FC
    @property
    def A(self) :
        return self.D + self.E
    @property
    def EBIT(self) :
        return self.S - self.C
    @property
    def Int(self) :
        return self.rD * self.D
    @property
    def EBT(self):
        return self.EBIT - self.Int
    @property
    def taxes(self):
        return self.EBT * self.tax
    @property
    def EAT(self):
        return self.EBT - self.taxes
    @property
    def ROA(self) :
        return self.EAT / self.A if self.A != 0 else 0.0
    @property
    def ROE(self) :
        return self.EAT / self.E if self.E != 0 else 0.0
    @property
    def ROS(self) :
        return self.EBIT / self.S if self.S != 0 else 0.0

    @staticmethod
    def classify_risk(roe: float):
        """
        Классификация ROE по интервалам :
        - A (1): ROE > 0.20-> Sq = 1
        - Б (2): 0.10 < ROE <= 0.20   -> Sq = 1
        """
        if roe > 0.20:
            return "A", 1, 1
        elif roe > 0.10:
            return "Б", 2, 1
        elif roe > 0.00:
            return "В", 3, 2
        elif roe > -0.10:
            return "Г", 4, 5
        else:
            return "Д", 5, 5

    @staticmethod
    def classify_prob(prob: float) :
        """
        - prob < 0.20 -> 1
        - 0.20 <= prob < 0.70 -> 2
        - prob >= 0.70 -> 3
        """
        if prob < 0.20:
            return 1
        elif prob < 0.70:
            return 2
        else:
            return 3

    def run_scenarios(self) :
        """Расчеты для заданных сценариев."""
        results = []
        for sc in self.scenarios:
            q = sc["Q"]
            p_prob = sc["prob"]
            s_sc = q * self.P
            c_sc = self.VC * q + self.FC
            ebit_sc = s_sc - c_sc
            ebt_sc = ebit_sc - self.Int
            eat_sc = ebt_sc * (1 - self.tax)
            roe_sc = eat_sc / self.E if self.E != 0 else 0.0
            cat, risk_code, sq = self.classify_risk(roe_sc)
            prob_score = self.classify_prob(p_prob)
            results.append({
                "Сценарий": sc["id"],
                "Q": q,
                "Вероятность": p_prob,
                "EBIT": round(ebit_sc, 2),
                "EAT (Чистая прибыль)": round(eat_sc, 2),
                "ROE": f"{roe_sc:.2%}",
                "ROE_raw": roe_sc,
                "Категория риска": cat,
                "Номер риска": risk_code,
                "Значимость (Sq)": sq,
                "Балл вероятности": prob_score
            })
        return pd.DataFrame(results)

    def analyze_scenario(self, scenario_id: int):
        """карточка конкретного сценария."""
        df = self.run_scenarios()
        matched = df[df["Сценарий"] == scenario_id]
        if matched.empty:
            print(f"Сценарий {scenario_id} не найден.")
            return
        row = matched.iloc[0]
        print(f"\n--- Детальный отчет: Сценарий {scenario_id} ---")
        print(f"Объем (Q):                {row['Q']}")
        print(f"Вероятность реализации:   {row['Вероятность']:.1%}")
        print(f"Операц. прибыль (EBIT):   {row['EBIT']}")
        print(f"Чистая прибыль (EAT):     {row['EAT (Чистая прибыль)']}")
        print(f"Рентабельность (ROE):     {row['ROE']}")
        print(f"Категория риска:          {row['Категория риска']} (Код: {row['Номер риска']})")
        print(f"Значимость риска (Sq):    {row['Значимость (Sq)']}")
        print(f"Балл вероятности (Prob):  {row['Балл вероятности']}")

model = RiskModel()
print("Базовый ROE:", f"{model.ROE:.2%}")
print("Базовый EBIT:", model.EBIT)
df = model.run_scenarios()
print(df[["Сценарий", "Q", "Вероятность", "ROE", "Категория риска", "Значимость (Sq)", "Балл вероятности"]])

model_fc350 = RiskModel(FC=350.0)
# Смотрим детально 2-й сценарий
model_fc350.analyze_scenario(2)

scenarios_with_4 = [
    {"id": 1, "Q": 80.0,  "prob": 0.20},
    {"id": 2, "Q": 100.0, "prob": 0.65},
    {"id": 3, "Q": 120.0, "prob": 0.10},
    {"id": 4, "Q": 65.0,  "prob": 0.05},
]
model_extended = RiskModel(FC=300.0, scenarios=scenarios_with_4)

# Вывод
print(model_extended.run_scenarios()[[
    "Сценарий", "Q", "Вероятность", "ROE", "Категория риска", "Значимость (Sq)", "Балл вероятности"
]])
model_extended.analyze_scenario(4)