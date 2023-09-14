const question = document.getElementById('question');
const A = document.getElementById('A');
const B = document.getElementById('B');
const C = document.getElementById('C');
const D = document.getElementById('D');
const E = document.getElementById('E');
const reset_button = document.getElementById('reset_button');
const submit_button = document.getElementById('submit_button');
const answer = document.getElementById('answer');

async function submit_mcq(event) {
    let data = {
        question: question.value,
        A: A.value,
        B: B.value,
        C: C.value,
        D: D.value,
        E: E.value
    };
    const res = await fetch('/mcq', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    let val = await res.json();
    answer.textContent = "The answer is " + val.answer;
}

reset_button.addEventListener('click', function () {
    question.value = '';
    A.value = '';
    B.value = '';
    C.value = '';
    D.value = '';
    E.value = '';
});
submit_button.addEventListener('click', submit_mcq);