document.addEventListener("DOMContentLoaded", function () {
  const question = document.getElementById("question");
  const A = document.getElementById("A");
  const B = document.getElementById("B");
  const C = document.getElementById("C");
  const D = document.getElementById("D");
  const E = document.getElementById("E");
  const submitButton = document.getElementById("submit_button");
  const clearButton = document.getElementById("reset_button");
  const selectedAnswer = document.getElementById("answer");
  const loadingElement = document.getElementById("loading");
  const prob = document.getElementById("prob");
  const imageElement = document.getElementById("image");
  let loadingInterval;

  imageElement.style.display = "none";
  const updateImage = (probability) => {
    if (probability >= 0.8) {
      imageElement.src = "/static/images/smile.jpg";
    } else if (probability >= 0.5) {
      imageElement.src = "/static/images/expressionless.jpg";
    } else {
      imageElement.src = "/static/images/angry.jpg";
    }
  };
  const handleSubmit = async () => {
    selectedAnswer.innerHTML = "";
    prob.innerHTML = "";
    imageElement.style.display = "none";
    const data = {
      question: question.value,
      A: A.value,
      B: B.value,
      C: C.value,
      D: D.value,
      E: E.value,
    };

    let emptyFieldCount = 0;

    if (A.value === "") emptyFieldCount++;
    if (B.value === "") emptyFieldCount++;
    if (C.value === "") emptyFieldCount++;
    if (D.value === "") emptyFieldCount++;
    if (E.value === "") emptyFieldCount++;
    if (question.value === "") {
      selectedAnswer.innerHTML = "문제를 입력하세요.";
    } else {
      if (emptyFieldCount === 5) {
        selectedAnswer.innerHTML = "객관식 답을 입력하세요.";
      } else if (emptyFieldCount >= 4) {
        selectedAnswer.innerHTML = "객관식 답을 2개 이상 입력하세요.";
      } else {
        loadingElement.style.display = "block";

        // 진행 중 타이머 clear
        if (loadingInterval) {
          clearInterval(loadingInterval);
        }

        // 로딩바 %초기화
        resetLoadingBar();
        document.getElementById("loading").classList.remove("hidden");

        let currentPercentage = 0;

        loadingInterval = setInterval(function () {
          currentPercentage++;
          updateLoadingBarAndPercentage(currentPercentage);
          if (currentPercentage >= 100) {
            clearInterval(loadingInterval);
          }
        }, 300);

        try {
          const res = await fetch("/mcq", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
          });

          if (res.ok) {
            const val = await res.json();
            selectedAnswer.innerHTML = `<h2>선택된 답은 ${val.answer}</h2>`;
            prob.innerHTML = "Probability : " + val.prob;
            updateImage(val.prob);
            imageElement.style.display = "block";
          } else {
            selectedAnswer.innerHTML =
              "<p>Error occurred while fetching the answer.</p>";
          }
        } catch (error) {
          console.error("에러가 발생했습니다: ", error);
          selectedAnswer.innerHTML =
            "<p>Error occurred while fetching the answer.</p>";
        } finally {
          loadingElement.style.display = "none";
        }
      }
    }
  };

  const handleClear = () => {
    question.value = "";
    A.value = "";
    B.value = "";
    C.value = "";
    D.value = "";
    E.value = "";
    selectedAnswer.innerHTML = "";
    prob.innerHTML = "";
    imageElement.style.display = "none";
  };

  function updateLoadingBarAndPercentage(percentage) {
    document.getElementById("loadingBar").style.width = percentage + "%";
    document.getElementById("loadingPercentage").textContent = percentage + "%";
  }

  function resetLoadingBar() {
    document.getElementById("loadingBar").style.width = "0%";
    document.getElementById("loadingPercentage").textContent = "0%";
  }

  submitButton.addEventListener("click", handleSubmit);
  clearButton.addEventListener("click", handleClear);
});
