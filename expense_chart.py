import csv
import sys
import os
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# 統一配色（對應範例圖表：藍、橘、綠、黃、粉紅，並擴充至 8 色）
PALETTE = [
    "#2374D8",  # Blue (Shopping)
    "#EA662D",  # Orange (Food)
    "#18AC6E",  # Green (Education)
    "#E7A100",  # Yellow/Gold (Entertainment)
    "#E5729F",  # Pink (Transport)
    "#8A5CF6",  # Purple
    "#06B6D4",  # Cyan
    "#64748B",  # Slate Gray (Other)
]


def load_expenses(csv_path="expenses.csv"):
    """讀取 CSV 檔案並依類別加總金額，由高到低排序。"""
    totals = defaultdict(float)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"找不到資料檔案：{csv_path}")

    with open(csv_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = (row.get("category") or "Uncategorized").strip()
            try:
                amount = float(row.get("amount", 0))
            except ValueError:
                continue
            if amount > 0:
                totals[category] += amount

    # 依金額由大到小排序
    sorted_items = sorted(totals.items(), key=lambda x: x[1], reverse=True)

    # 若超過 8 類，將第 8 類之後合併為 Other
    if len(sorted_items) > 8:
        top_seven = sorted_items[:7]
        other_sum = sum(val for _, val in sorted_items[7:])
        sorted_items = top_seven + [("Other", other_sum)]

    return sorted_items


def _format_num(val):
    """若為整數則去掉小數點，否則保留兩位小數並加上千分位逗號。"""
    if float(val).is_integer():
        return f"{int(round(val)):,}"
    return f"{val:,.2f}"


def generate_pie_chart(csv_path="expenses.csv", output_path="pie_chart.png"):
    """產生甜甜圈圖（Donut Chart），含中央總金額與右側圓點圖例。"""
    items = load_expenses(csv_path)
    if not items:
        raise ValueError("CSV 檔案中沒有有效的支出資料。")

    categories = [k for k, _ in items]
    amounts = [v for _, v in items]
    total_spent = sum(amounts)
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(categories))]

    fig, ax = plt.subplots(figsize=(9, 5.8), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # 繪製甜甜圈圖（從 12 點鐘方向順時針排列）
    wedges, _ = ax.pie(
        amounts,
        colors=colors,
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.37, edgecolor="white", linewidth=2.5),
    )

    # 中央總金額與 TOTAL SPENT 標籤
    ax.text(
        0, 0.05,
        _format_num(total_spent),
        ha="center", va="center",
        fontsize=26, fontweight="bold", color="#111111",
    )
    ax.text(
        0, -0.15,
        "TOTAL SPENT",
        ha="center", va="center",
        fontsize=10.5, color="#555555",
    )

    # 右側圓點圖例（顯示類別、金額與百分比）
    legend_handles = []
    for cat, amt, color in zip(categories, amounts, colors):
        pct = (amt / total_spent) * 100
        label = f"  {cat}   {_format_num(amt)}  ({pct:.1f}%)"
        handle = Line2D(
            [0], [0],
            marker="o", color="w", label=label,
            markerfacecolor=color, markersize=12,
        )
        legend_handles.append(handle)

    ax.legend(
        handles=legend_handles,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
        fontsize=11.5,
        labelspacing=1.25,
        handletextpad=0.6,
    )

    fig.suptitle(
        "Expenses by Category",
        x=0.04, y=0.95, ha="left",
        fontsize=17, fontweight="bold", color="#111111",
    )

    ax.set_aspect("equal")
    plt.subplots_adjust(left=0.04, right=0.58, top=0.84, bottom=0.06)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def generate_bar_chart(csv_path="expenses.csv", output_path="bar_chart.png"):
    """產生水平長條圖（Horizontal Bar Chart），含右側數值標籤。"""
    items = load_expenses(csv_path)
    if not items:
        raise ValueError("CSV 檔案中沒有有效的支出資料。")

    # 水平長條圖由下往上繪製，反轉順序讓最大金額顯示在最上方
    items_rev = list(reversed(items))
    categories = [k for k, _ in items_rev]
    amounts = [v for _, v in items_rev]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(items) - 1, -1, -1)]

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    bars = ax.barh(categories, amounts, color=colors, height=0.55)

    # 隱藏上、右、下邊框與 X 軸刻度，僅保留左側細灰線
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["left"].set_linewidth(1.0)
    ax.xaxis.set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=12, pad=8, colors="#111111")

    # 在每條長條右側加上金額數字
    max_amt = max(amounts) if amounts else 1
    ax.set_xlim(0, max_amt * 1.16)
    for bar, amt in zip(bars, amounts):
        ax.text(
            bar.get_width() + max_amt * 0.018,
            bar.get_y() + bar.get_height() / 2,
            _format_num(amt),
            va="center", ha="left",
            fontsize=11.5, color="#111111",
        )

    ax.set_title(
        "Spending per Category",
        loc="left", pad=18,
        fontsize=17, fontweight="bold", color="#111111",
    )

    plt.subplots_adjust(left=0.18, right=0.94, top=0.86, bottom=0.06)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def generate_charts(csv_path="expenses.csv"):
    """同時產生圓餅圖與長條圖（供單獨執行與網頁介面呼叫）。"""
    pie_file = generate_pie_chart(csv_path, "pie_chart.png")
    bar_file = generate_bar_chart(csv_path, "bar_chart.png")
    return pie_file, bar_file


if __name__ == "__main__":
    target_csv = sys.argv[1] if len(sys.argv) > 1 else "expenses.csv"
    if not os.path.exists(target_csv) and os.path.exists("sample_expenses.csv"):
        target_csv = "sample_expenses.csv"

    pie_out, bar_out = generate_charts(target_csv)
    print(f"已產生圖表：{pie_out}, {bar_out}")
