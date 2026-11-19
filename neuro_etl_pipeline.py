import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Tabela 1: Metadane uczestników eksperymentu
df_participants = pd.DataFrame({
    'participant_id': [201, 202, 203, 204, 205],
    'full_name': [' jan kowalski ', 'ANNA NOWAK', ' piotr wiśniewski', 'katarzyna wójcik ', 'tomasz lewandowski'],
    'age': [22.0, 29.0, np.nan, 35.0, 26.0],
    'protocol': ['Neurofeedback', 'Kontrola', 'Neurofeedback', 'Kontrola', 'Neurofeedback'],
    'baseline_stress': [7.0, 5.0, 8.0, np.nan, 6.0]
})

# Tabela 2: Surowe logi z czepka EEG (uwaga: wiersze są w losowej kolejności!)
df_sessions = pd.DataFrame({
    'session_id': ['S01', 'S02', 'S03', 'S04', 'S05', 'S06', 'S07', 'S08', 'S09', 'S10'],
    'subject_id': [201, 202, 201, 203, 201, 202, 204, 203, 204, 202],
    'recorded_at': ['2026-11-02', '2026-11-02', '2026-11-05', '2026-11-03', '2026-11-08',
                    '2026-11-06', '2026-11-04', '2026-11-07', '2026-11-08', '2026-11-10'],
    'session_no': [1, 1, 2, 1, 3, 2, 1, 2, 2, 3],
    'alpha_power': [8.5, 9.0, 10.2, 7.4, 11.8, 9.1, 8.0, 9.6, 8.3, 8.9],
    'signal_noise_pct': [10, 12, 8, 28, 6, 15, 9, 11, 22, 14]
})
#1
df_participants['full_name'] = df_participants['full_name'].str.strip().str.title()
df_participants['age'] = df_participants['age'].fillna(df_participants['age'].mean()).astype('int16')
df_participants['baseline_stress'] = df_participants['baseline_stress'].fillna(df_participants['baseline_stress'].mean()).astype('float32')
#2
df_study = pd.merge(
    df_participants,
    df_sessions,
    left_on='participant_id',
    right_on='subject_id',
    how='inner'
)
df_study = df_study.drop(columns='subject_id')

df_study['recorded_at'] = pd.to_datetime(df_study['recorded_at'])
df_study['day_name'] = df_study['recorded_at'].dt.day_name()
df_study['is_weekend'] = df_study['recorded_at'].dt.day_of_week >= 5

#3
df_study = df_study.sort_values(['participant_id', 'session_no'], ascending=True)
df_study['protocol_avg_alpha'] = df_study.groupby('protocol')['alpha_power'].transform('mean')
df_study['alpha_vs_protocol'] = df_study['alpha_power'] - df_study['protocol_avg_alpha']
df_study['prev_alpha'] = df_study.groupby('participant_id')['alpha_power'].shift(1)
df_study['alpha_delta'] = df_study['alpha_power'] - df_study['prev_alpha']
pd.set_option('display.max_columns', None)
#4
df_study['quality_flag'] = np.where(df_study['signal_noise_pct'] > 20, 'odrzuc', 'OK')
def classify_alha(val):
    if val < 8.5:
        return 'Rozproszenie'
    elif 8.5 <= val < 10.5:
        return 'Spokoj'
    else:
        return 'Gleboki relaks'
df_study['neuro_state'] = df_study['alpha_power'].apply(classify_alha)
df_study['protocol'] = df_study['protocol'].astype('category')
df_study['day_name'] = df_study['day_name'].astype('category')
df_study['quality_flag'] = df_study['quality_flag'].astype('category')
df_study['neuro_state'] = df_study['neuro_state'].astype('category')
#5
df_clean = df_study[df_study['quality_flag'] == 'OK']
protocol_summary = df_clean.groupby('protocol').agg(
    mean_alpha = ('alpha_power', 'mean'),
    max_alpa = ('alpha_power', 'max'),
    valid_sessions = ('session_no', 'count')
)
print(df_study)
print("="*50)
print(df_clean)
print("="*50)
print(protocol_summary)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,4.5))
sns.boxplot(data=df_clean,x='protocol', y='alpha_power',hue='protocol',palette='Set2',ax=ax1)
ax1.set_title('Porownanie mocy alpha do protokołu')
ax1.set_xlabel('protocol')
ax1.set_ylabel('alpha_power')
sns.lineplot(data=df_clean, x='session_no',y='alpha_power',hue='protocol',marker='o', ax=ax2)
ax2.set_title('Przebieg mocy alpha w kolejnych sesjach')
ax2.set_xlabel('numer sesji')
ax2.set_ylabel('alpha power')
plt.tight_layout()
fig.savefig('chart_summary.png', dpi=150)
plt.show()