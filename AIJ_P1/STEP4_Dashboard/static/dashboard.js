
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
        
        // 현재 선택된 개표 단계 확인
        const stepSelect = document.getElementById("step-select");

        const currentStep = stepSelect
            ? Number(stepSelect.value)
            : 1;

        // 현재 단계까지의 개표 데이터만 표시
        const steps = [...new Set(
            result.data
                .map(row => Number(row.step))
                .filter(step => step <= currentStep)
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


/* ==========================================
   STEP 5-21: WebSocket 개표 제어 기능
   ========================================== */

let electionWS = null;

// 상태 표시 함수
function updateWSStatus(id, message) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = message;
    }
}

// WebSocket 연결
function connectElectionWS() {
    const protocol =
        location.protocol === "https:" ? "wss:" : "ws:";

    const wsUrl = `${protocol}//${location.host}/ws`;

    electionWS = new WebSocket(wsUrl);

    // 연결 성공
    
electionWS.onopen = () => {
    // 서버 연결 성공 표시
    updateWSStatus(
        "ws-connection-status",
        "연결됨"
    );

    // 이전 연결 오류 메시지 제거
    updateWSStatus(
        "ws-error-message",
        ""
    );

    console.log("WebSocket 연결 성공");
};


    // 서버 데이터 수신
    electionWS.onmessage = (event) => {
        const result = JSON.parse(event.data);

        
if (result.type === "election_update") {

    // 현재 개표 단계 표시
    updateWSStatus(
        "ws-current-step",
        `${result.step} / 10`
    );

    // 재생 상태 표시
    updateWSStatus(
        "ws-playback-status",
        "개표 진행 중"
    );

    // 기존 대시보드의 단계 선택값 변경
    const stepSelect = document.getElementById("step-select");

    
if (stepSelect) {
    stepSelect.value = String(result.step);

    // 현재 선택된 단계 정보 표시
    const stepInfo = document.getElementById(
        "selected-step-info"
    );

    if (stepInfo) {
        stepInfo.textContent =
            `현재 조회 단계: ${result.step}단계`;
    }

    // 기존 대시보드 데이터 갱신
    loadElectionResults();
    loadRegionResults();

    // Plotly 득표율 그래프 갱신
    loadVoteChart();
}


    console.log(
        `개표 ${result.step}/10 단계 수신`,
        result.data
    );
}


        else if (result.type === "playback_status") {
            const statusText = {
                paused: "일시정지",
                playing: "개표 진행 중",
                reset: "대기 중"
            };

            updateWSStatus(
                "ws-playback-status",
                statusText[result.status] || result.status
            );

            updateWSStatus(
                "ws-current-step",
                `${result.step} / 10`
            );

            // 개표 초기화 시 화면 데이터 초기화
            if (result.status === "reset") {

                // 단계 선택값 초기화
                const stepSelect = document.getElementById(
                    "step-select"
                );

                if (stepSelect) {
                    stepSelect.value = "1";
                }

                // 현재 조회 단계 안내 변경
                updateWSStatus(
                    "selected-step-info",
                    "개표 대기 중"
                );

                // 후보별 개표 결과 초기화
                const candidateContainer = document.getElementById(
                    "candidate-results"
                );

                if (candidateContainer) {
                    candidateContainer.innerHTML =
                        "<p>개표 시작 전입니다.</p>";
                }

                // 지역별 결과 초기화
                const regionContainer = document.getElementById(
                    "region-results"
                );

                if (regionContainer) {
                    regionContainer.innerHTML =
                        "<p>개표 시작 전입니다.</p>";
                }

                // Plotly 그래프 초기화
                const chartContainer = document.getElementById(
                    "vote-chart"
                );

                if (chartContainer && typeof Plotly !== "undefined") {
                    Plotly.purge(chartContainer);
                    chartContainer.innerHTML =
                        "<p style='color:#cbd5e1; padding:20px;'>" +
                        "개표가 시작되면 그래프가 표시됩니다." +
                        "</p>";
                }

                console.log("개표 화면 초기화 완료");
            }

        }

        else if (result.type === "election_complete") {
            updateWSStatus(
                "ws-playback-status",
                "개표 완료"
            );
        }

        else if (result.type === "error") {
            updateWSStatus(
                "ws-error-message",
                result.message
            );
        }
    };

    // 연결 오류
    electionWS.onerror = () => {
        updateWSStatus(
            "ws-error-message",
            "WebSocket 연결 오류가 발생했습니다."
        );
    };

    // 연결 종료
    
    // 서버 연결 종료 시 자동 재연결
    electionWS.onclose = () => {
        updateWSStatus(
            "ws-connection-status",
            "연결 종료 · 재연결 시도 중"
        );

        // 3초 후 WebSocket 연결 재시도
        setTimeout(() => {
            // 이미 연결되어 있다면 중복 연결하지 않음
            if (
                !electionWS ||
                electionWS.readyState === WebSocket.CLOSED
            ) {
                console.log("WebSocket 재연결 시도");
                connectElectionWS();
            }
        }, 3000);
    };

}

// 명령 전송
function sendElectionCommand(command) {
    if (!electionWS || electionWS.readyState !== WebSocket.OPEN) {
        updateWSStatus(
            "ws-error-message",
            "WebSocket 서버에 연결되어 있지 않습니다."
        );
        return;
    }

    updateWSStatus("ws-error-message", "");
    electionWS.send(command);
}

// 버튼 이벤트 연결
function initializeElectionControls() {
    const buttons = {
        "ws-start-btn": "start",
        "ws-pause-btn": "pause",
        "ws-resume-btn": "resume",
        "ws-reset-btn": "reset"
    };

    for (const [buttonId, command] of Object.entries(buttons)) {
        const button = document.getElementById(buttonId);

        if (button) {
            button.addEventListener("click", () => {
                sendElectionCommand(command);
            });
        }
    }

    // 버튼 준비 후 WebSocket 연결
    connectElectionWS();
}

// HTML 화면이 준비되면 초기화
if (document.readyState === "loading") {
    document.addEventListener(
        "DOMContentLoaded",
        initializeElectionControls
    );
} else {
    initializeElectionControls();
}
