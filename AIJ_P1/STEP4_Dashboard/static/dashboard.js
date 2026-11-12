
async function loadElectionResults() {
    const container = document.getElementById("candidate-results");

    try {
        // FastAPI에서 가상 선거 데이터 가져오기
        const response = await fetch("/api/election-results");

        if (!response.ok) {
            throw new Error("서버 응답 오류: " + response.status);
        }

        const result = await response.json();

        // 마지막 개표 단계 확인
        const finalStep = Number(
    document.getElementById("step-select").value
);

        // 마지막 단계의 후보별 데이터 합산
        const finalRows = result.data.filter(
            row => Number(row.step) === finalStep
        );

        const candidates = {};

        finalRows.forEach(row => {
            const name = row.candidate_name;

            if (!candidates[name]) {
                candidates[name] = 0;
            }

            candidates[name] += Number(row.votes);
        });

        const totalVotes = Object.values(candidates)
            .reduce((sum, votes) => sum + votes, 0);

        // 득표수가 많은 순서로 정렬
        const ranking = Object.entries(candidates)
            .sort((a, b) => b[1] - a[1]);

        const colors = {
            "이몽룡": "#3b82f6",
            "심청이": "#ef4444",
            "홍길동": "#22c55e"
        };

        // HTML 화면에 결과 출력
        container.innerHTML = ranking.map(([name, votes], index) => {
            const percentage = totalVotes > 0
                ? (votes / totalVotes * 100).toFixed(2)
                : "0.00";

            const color = colors[name] || "#94a3b8";

            return `
                <div style="margin-bottom: 25px;">
                    <h3>${index + 1}위 · ${name}</h3>
                    <p>${votes.toLocaleString("ko-KR")}표 · ${percentage}%</p>
                    <div style="background:#334155; border-radius:6px;">
                        <div style="
                            width:${percentage}%;
                            height:18px;
                            background:${color};
                            border-radius:6px;
                        "></div>
                    </div>
                </div>
            `;
        }).join("");

        console.log("후보별 개표 데이터 로드 완료");

    } catch (error) {
        console.error(error);
        container.textContent = "개표 데이터를 불러오지 못했습니다.";
    }
}

document.addEventListener("DOMContentLoaded", loadElectionResults);


async function loadRegionResults() {
    const container = document.getElementById("region-results");

    try {
        const response = await fetch("/api/election-results");

        if (!response.ok) {
            throw new Error("서버 응답 오류: " + response.status);
        }

        const result = await response.json();

        // 마지막 개표 단계 확인
        const finalStep = Number(
    document.getElementById("step-select").value
);

        const finalRows = result.data.filter(
            row => Number(row.step) === finalStep
        );

        // 지역별, 후보별 득표수 정리
        const regions = {};

        finalRows.forEach(row => {
            const region = row.region;
            const candidate = row.candidate_name;

            if (!regions[region]) {
                regions[region] = {};
            }

            regions[region][candidate] =
                (regions[region][candidate] || 0) + Number(row.votes);
        });

        const regionOrder = [
            "중앙구", "동부구", "서부구", "남부구", "북부구"
        ];

        const candidateOrder = ["이몽룡", "심청이", "홍길동"];

        // HTML 표 생성
        const tableRows = regionOrder.map(region => {
            const votes = regions[region] || {};

            const cells = candidateOrder.map(candidate => {
                const count = votes[candidate] || 0;
                return `<td>${count.toLocaleString("ko-KR")}</td>`;
            }).join("");

            return `<tr><th scope="row">${region}</th>${cells}</tr>`;
        }).join("");

        container.innerHTML = `
            <div style="overflow-x:auto;">
                <table class="election-table">
                    <thead>
                        <tr>
                            <th>지역</th>
                            <th>이몽룡</th>
                            <th>심청이</th>
                            <th>홍길동</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableRows}
                    </tbody>
                </table>
            </div>
            <p>최종 개표 단계: ${finalStep}단계</p>
        `;

        console.log("지역별 개표 현황 로드 완료");

    } catch (error) {
        console.error(error);
        container.textContent = "지역별 데이터를 불러오지 못했습니다.";
    }
}

document.addEventListener("DOMContentLoaded", loadRegionResults);


async function loadVoteChart() {
    const container = document.getElementById("vote-chart");

    try {
        const response = await fetch("/api/election-results");

        if (!response.ok) {
            throw new Error("서버 응답 오류: " + response.status);
        }

        const result = await response.json();

        const candidateNames = ["이몽룡", "심청이", "홍길동"];

        const colors = {
            "이몽룡": "#3b82f6",
            "심청이": "#ef4444",
            "홍길동": "#22c55e"
        };

        // 개표 단계를 숫자 순서로 정렬
        const steps = [...new Set(
            result.data.map(row => Number(row.step))
        )].sort((a, b) => a - b);

        // 개표 단계별 후보 득표수 합산
        const traces = candidateNames.map(name => {
            const percentages = steps.map(step => {
                const stepRows = result.data.filter(
                    row => Number(row.step) === step
                );

                const totalVotes = stepRows.reduce(
                    (sum, row) => sum + Number(row.votes), 0
                );

                const candidateVotes = stepRows
                    .filter(row => row.candidate_name === name)
                    .reduce(
                        (sum, row) => sum + Number(row.votes), 0
                    );

                return totalVotes > 0
                    ? candidateVotes / totalVotes * 100
                    : 0;
            });

            return {
                x: steps,
                y: percentages,
                mode: "lines+markers",
                name: name,
                line: {
                    color: colors[name],
                    width: 3
                },
                marker: {
                    size: 7
                },
                hovertemplate:
                    "개표 %{x}단계<br>" +
                    name + ": %{y:.2f}%<extra></extra>"
            };
        });

        const layout = {
            title: {
                text: "개표 단계별 후보 득표율 변화",
                font: { color: "#ffffff", size: 18 }
            },
            paper_bgcolor: "#0f1d30",
            plot_bgcolor: "#0f1d30",
            font: { color: "#cbd5e1" },
            xaxis: {
                title: "개표 단계",
                tickmode: "array",
                tickvals: steps,
                gridcolor: "#334155"
            },
            yaxis: {
                title: "득표율 (%)",
                ticksuffix: "%",
                gridcolor: "#334155",
                rangemode: "tozero"
            },
            legend: {
                orientation: "h",
                x: 0,
                y: -0.3
            },
            margin: {
                l: 55, r: 20, t: 65, b: 80
            },
            autosize: true
        };

        await Plotly.newPlot(
            container,
            traces,
            layout,
            {
                responsive: true,
                displaylogo: false
            }
        );

        console.log("득표율 변화 그래프 표시 완료");

    } catch (error) {
        console.error(error);
        container.textContent = "그래프를 표시하지 못했습니다.";
    }
}

document.addEventListener("DOMContentLoaded", loadVoteChart);


document.addEventListener("DOMContentLoaded", () => {
    const stepSelect = document.getElementById("step-select");
    const stepInfo = document.getElementById("selected-step-info");

    stepSelect.addEventListener("change", () => {
        const selectedStep = stepSelect.value;

        // 현재 선택한 개표 단계 표시
        stepInfo.textContent =
            `현재 조회 단계: ${selectedStep}단계`;

        // 선택한 단계의 후보별 개표 데이터 다시 계산
        loadElectionResults();

        // 선택한 단계의 지역별 개표 데이터 다시 계산
        loadRegionResults();

        console.log(`개표 ${selectedStep}단계 조회 완료`);
    });
});


function highlightSelectedStep() {
    const chart = document.getElementById("vote-chart");
    const step = Number(
        document.getElementById("step-select").value
    );

    // Plotly 그래프가 생성되었는지 확인
    if (!chart || !chart.data) {
        return;
    }

    // 선택한 개표 단계에 노란색 세로선 표시
    Plotly.relayout(chart, {
        shapes: [{
            type: "line",
            xref: "x",
            yref: "paper",
            x0: step,
            x1: step,
            y0: 0,
            y1: 1,
            line: {
                color: "#facc15",
                width: 2,
                dash: "dash"
            }
        }]
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const stepSelect = document.getElementById("step-select");

    stepSelect.addEventListener("change", highlightSelectedStep);

    // 최초 그래프 생성 시의 선택 단계는 별도 연동 예정
});
