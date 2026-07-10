import json
from pathlib import Path


path = Path(__file__).with_name("student_performance.ipynb")
nb = json.loads(path.read_text(encoding="utf-8"))

old_start = "# ---------- FinalGrade Distribution ----------"
old_end = "# ---------- Online Classes Taken pie chart ----------"

replacement = '''# ---------- FinalGrade Distribution ----------
ax2 = fig.add_subplot(gs[2, 0:3])
grade_bins = [-0.01, 59, 69, 79, 89, 100]
grade_labels = ['0-59', '60-69', '70-79', '80-89', '90-100']
plot_df = df.copy()
grades = []

if 'FinalGrade' in plot_df.columns:
    plot_df['FinalGradeNumeric'] = pd.to_numeric(plot_df['FinalGrade'], errors='coerce')
    plot_df = plot_df[plot_df['FinalGradeNumeric'].between(0, 100)]
    plot_df['FinalGradeRange'] = pd.cut(
        plot_df['FinalGradeNumeric'],
        bins=grade_bins,
        labels=grade_labels,
        include_lowest=True
    )
    grade_counts = plot_df['FinalGradeRange'].value_counts().reindex(grade_labels, fill_value=0)
    colors_rainbow = sns.color_palette('rainbow', n_colors=len(grade_labels))

    bars = ax2.bar(
        grade_labels,
        grade_counts.values,
        color=colors_rainbow,
        edgecolor='white',
        linewidth=1.2
    )
    max_count = max(grade_counts.max(), 1)
    ax2.set_ylim(0, max_count * 1.18)
    ax2.bar_label(
        bars,
        labels=[str(int(v)) for v in grade_counts.values],
        padding=4,
        fontsize=12,
        fontweight='bold',
        color='white'
    )
else:
    plot_df = pd.DataFrame()
    colors_rainbow = sns.color_palette('rainbow', n_colors=len(grade_labels))

ax2.set_title('Distribution by Final Grade', fontsize=18, fontweight='bold', color='#00e5ff', pad=12)
ax2.set_facecolor('#0f1626')
ax2.set_xlabel('Final Grade Range', fontsize=13, color='white', labelpad=8)
ax2.set_ylabel('Number of Students', fontsize=13, color='white', labelpad=8)
ax2.tick_params(axis='x', labelrotation=0, labelsize=11, colors='white')
ax2.tick_params(axis='y', labelsize=11, colors='white')
ax2.margins(x=0.04)
ax2.grid(axis='y', linestyle='--', alpha=0.3)
for spine in ax2.spines.values():
    spine.set_edgecolor('#00e5ff')
    spine.set_linewidth(1.5)

# ---------- Average Study Hours by Grade Range ----------
ax3 = fig.add_subplot(gs[2, 3:5])
if not plot_df.empty and 'Study Hours' in plot_df.columns:
    plot_df['StudyHoursNumeric'] = pd.to_numeric(plot_df['Study Hours'], errors='coerce')
    study_plot_df = plot_df[
        plot_df['StudyHoursNumeric'].between(0, 24)
    ].dropna(subset=['FinalGradeRange', 'StudyHoursNumeric'])
    study_summary = study_plot_df.groupby('FinalGradeRange', observed=False)['StudyHoursNumeric'].agg(['mean', 'count'])
    study_summary = study_summary.reindex(grade_labels).fillna(0)

    bars = ax3.bar(
        grade_labels,
        study_summary['mean'].values,
        color=colors_rainbow,
        edgecolor='white',
        linewidth=1.2
    )
    max_hours = max(study_summary['mean'].max(), 1)
    ax3.set_ylim(0, max_hours * 1.35)
    ax3.bar_label(
        bars,
        labels=[f"{value:.1f}h" if count else "0h" for value, count in zip(study_summary['mean'], study_summary['count'])],
        padding=4,
        fontsize=11,
        fontweight='bold',
        color='white'
    )
    for index, count in enumerate(study_summary['count']):
        ax3.text(
            index,
            max_hours * 0.05,
            f"n={int(count)}",
            ha='center',
            va='bottom',
            fontsize=9,
            color='#d9f7ff',
            fontweight='bold'
        )

ax3.set_title('Average Study Hours by Final Grade', fontsize=16, fontweight='bold', color='#00e5ff', pad=12)
ax3.set_facecolor('#0f1626')
ax3.set_xlabel('Final Grade Range', fontsize=12, color='white', labelpad=8)
ax3.set_ylabel('Average Study Hours', fontsize=12, color='white', labelpad=8)
ax3.tick_params(axis='x', labelrotation=0, labelsize=10, colors='white')
ax3.tick_params(axis='y', labelsize=10, colors='white')
ax3.margins(x=0.04)
ax3.grid(axis='y', linestyle='--', alpha=0.3)
for spine in ax3.spines.values():
    spine.set_edgecolor('#00e5ff')
    spine.set_linewidth(1.5)

'''

updated = False
for index, cell in enumerate(nb["cells"]):
    if cell.get("cell_type") != "code":
        continue

    source = "".join(cell.get("source", []))
    if old_start not in source or old_end not in source:
        continue

    start_index = source.index(old_start)
    end_index = source.index(old_end)
    new_source = source[:start_index] + replacement + source[end_index:]
    new_source = new_source.replace(
        "plt.tight_layout()\nplt.show()",
        "fig.subplots_adjust(left=0.055, right=0.975, top=0.91, bottom=0.055, hspace=0.55, wspace=0.35)\nplt.show()",
    )
    cell["source"] = [line + "\n" for line in new_source.splitlines()]
    updated = True
    print(f"Updated dashboard plotting block in cell {index}")
    break

if not updated:
    raise SystemExit("Target plotting block not found.")

path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
