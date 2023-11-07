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
  const smileImage = document.getElementById("smile_image");
  const expressionlessImage = document.getElementById("expressionless_image");
  const angryImage = document.getElementById("angry_image");

  const updateImage = (probability) => {
    if (probability >= 0.8) {
      smileImage.style.opacity = 1;
      expressionlessImage.style.opacity = 0.1;
      angryImage.style.opacity = 0.1;
    } else if (probability >= 0.5) {
      smileImage.style.opacity = 0.1;
      expressionlessImage.style.opacity = 1;
      angryImage.style.opacity = 0.1;
    } else {
      smileImage.style.opacity = 0.1;
      expressionlessImage.style.opacity = 0.1;
      angryImage.style.opacity = 1;
    }
  };
  const handleSubmit = async () => {
    selectedAnswer.innerHTML = "";
    loadingElement.style.display = "none";
    smileImage.style.opacity = 1;
    expressionlessImage.style.opacity = 1;
    angryImage.style.opacity = 1;
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
      selectedAnswer.innerHTML = "<h1>문제를 입력하세요.</h1>";
    } else {
      if (emptyFieldCount === 5) {
        selectedAnswer.innerHTML = "<h1>객관식 답을 입력하세요.</h1>";
      } else if (emptyFieldCount >= 4) {
        selectedAnswer.innerHTML = "<h1>객관식 답을 2개 이상 입력하세요.</h1>";
      } else {
        loadingElement.style.display = "block";

        try {
          const res = await fetch("/mcq", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
          });

          if (res.ok) {
            const val = await res.json();
            selectedAnswer.innerHTML = `<h1>선택된 답은 ${val.answer}</h1>`;
            updateImage(val.prob);
          } else {
            selectedAnswer.innerHTML =
              "<h2>Error occurred while fetching the answer.</h2>";
          }
        } catch (error) {
          console.error("에러가 발생했습니다: ", error);
          selectedAnswer.innerHTML =
            "<h1>Error occurred while fetching the answer.</h1>";
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
    loadingElement.style.display = "none";
    smileImage.style.opacity = 1;
    expressionlessImage.style.opacity = 1;
    angryImage.style.opacity = 1;
  };

  question.addEventListener("focus", function () {
    this.style.height = "auto";
    this.style.height = this.scrollHeight + "px";
    this.classList.remove("initial-height");
  });
  question.addEventListener("blur", function () {
    this.style.height = "4em";
    this.classList.add("initial-height");
  });
  A.addEventListener("focus", function () {
    this.style.height = "auto";
    this.style.height = this.scrollHeight + "px";
    this.classList.remove("initial-height");
  });
  A.addEventListener("blur", function () {
    this.style.height = "4em";
    this.classList.add("initial-height");
  });
  B.addEventListener("focus", function () {
    this.style.height = "auto";
    this.style.height = this.scrollHeight + "px";
    this.classList.remove("initial-height");
  });
  B.addEventListener("blur", function () {
    this.style.height = "4em";
    this.classList.add("initial-height");
  });
  C.addEventListener("focus", function () {
    this.style.height = "auto";
    this.style.height = this.scrollHeight + "px";
    this.classList.remove("initial-height");
  });
  C.addEventListener("blur", function () {
    this.style.height = "4em";
    this.classList.add("initial-height");
  });
  D.addEventListener("focus", function () {
    this.style.height = "auto";
    this.style.height = this.scrollHeight + "px";
    this.classList.remove("initial-height");
  });
  D.addEventListener("blur", function () {
    this.style.height = "4em";
    this.classList.add("initial-height");
  });
  E.addEventListener("focus", function () {
    this.style.height = "auto";
    this.style.height = this.scrollHeight + "px";
    this.classList.remove("initial-height");
  });
  E.addEventListener("blur", function () {
    this.style.height = "4em";
    this.classList.add("initial-height");
  });

  submitButton.addEventListener("click", handleSubmit);
  clearButton.addEventListener("click", handleClear);
});
