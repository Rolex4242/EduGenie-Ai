
const tabs = {

    qa: {
        label: "Ask EduGenie a question",
        placeholder: "Why is the sky blue?",
        button: "Get Answer"
    },

    explain: {
        label: "What would you like explained?",
        placeholder: "Photosynthesis",
        button: "Explain"
    },

    summarize: {
        label: "Paste text to summarize",
        placeholder: "Paste your notes or paragraph here...",
        button: "Summarize"
    },

    quiz: {
        label: "Generate a quiz about",
        placeholder: "Pythagorean theorem",
        button: "Generate Quiz"
    },

    learn: {
        label: "Build a learning path for",
        placeholder: "Python programming",
        button: "Get Recommendations"
    }

};


let active = "qa";


const input = document.querySelector("#input");

const result = document.querySelector("#result");

const submit = document.querySelector("#submit");

const label = document.querySelector("#label");


// -----------------------------
// CHANGE MODULE
// -----------------------------

function setTab(tab) {

    active = tab;

    document.querySelectorAll("nav button").forEach(button => {

        button.classList.toggle(
            "active",
            button.dataset.tab === tab
        );

    });

    label.textContent = tabs[tab].label;

    input.placeholder = tabs[tab].placeholder;

    input.value = "";

    result.innerHTML = "";

    submit.textContent = tabs[tab].button + " →";

}


document.querySelectorAll("nav button").forEach(button => {

    button.addEventListener("click", () => {

        setTab(button.dataset.tab);

    });

});


// -----------------------------
// DISPLAY TEXT RESPONSE
// -----------------------------

function showResponse(text) {

    result.innerHTML = "";

    const box = document.createElement("div");

    box.className = "answer";

    box.textContent = text;

    result.appendChild(box);

}


// -----------------------------
// FORM SUBMISSION
// -----------------------------

document.querySelector("#form").addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();

        const value = input.value.trim();

        if (!value) {
            return;
        }

        submit.disabled = true;

        submit.textContent = "Working...";

        result.textContent = "Thinking... Please wait.";

        try {

            let data;


            // LEARNING PATH

            if (active === "learn") {

                const url =
                    "/api/learn/recommendations?topic=" +
                    encodeURIComponent(value);

                const response = await fetch(url);

                data = await response.json();

                if (!response.ok) {
                    throw new Error(
                        data.detail || "Request failed"
                    );
                }

                showResponse(data.recommendation);

            }


            // OTHER MODULES

            else {

                const endpoint = {

                    qa: "qa",

                    explain: "explain",

                    summarize: "summarize",

                    quiz: "quiz"

                }[active];


                const key = {

                    qa: "question",

                    explain: "topic",

                    summarize: "text",

                    quiz: "topic"

                }[active];


                const response = await fetch(
                    "/api/" + endpoint,
                    {

                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            [key]: value
                        })

                    }
                );


                data = await response.json();

                if (!response.ok) {
                    throw new Error(
                        data.detail || "Request failed"
                    );
                }


                if (active === "quiz") {

                    renderQuiz(data.quiz);

                }

                else {

                    showResponse(
                        data.answer ||
                        data.explanation ||
                        data.summary
                    );

                }

            }

        }

        catch (error) {

            showResponse(
                "Something went wrong: " + error.message
            );

        }

        finally {

            submit.disabled = false;

            submit.textContent =
                tabs[active].button + " →";

        }

    }
);


// -----------------------------
// QUIZ RENDERING
// -----------------------------

function renderQuiz(questions) {

    result.innerHTML = "";

    questions.forEach((question, index) => {

        const card = document.createElement("div");

        card.className = "answer";


        const title = document.createElement("p");

        title.className = "question";

        title.textContent =
            `Q${index + 1}. ${question.question}`;

        card.appendChild(title);


        question.options.forEach((option, optionIndex) => {

            const optionLabel = document.createElement("label");

            optionLabel.className = "option";


            const radio = document.createElement("input");

            radio.type = "radio";

            radio.name = "question" + index;

            radio.value = optionIndex;


            optionLabel.appendChild(radio);

            optionLabel.appendChild(
                document.createTextNode(" " + option)
            );

            card.appendChild(optionLabel);

        });


        const button = document.createElement("button");

        button.className = "submit";

        button.textContent = "Check Answer";


        button.addEventListener("click", () => {

            const selected = card.querySelector(
                "input:checked"
            );

            const oldFeedback = card.querySelector(".feedback");

            if (oldFeedback) {
                oldFeedback.remove();
            }


            const feedback = document.createElement("p");

            feedback.className = "feedback";


            if (!selected) {

                feedback.textContent =
                    "Please select an answer first.";

            }

            else if (
                Number(selected.value) === question.answer
            ) {

                feedback.textContent =
                    "Correct! " + (question.explanation || "");

            }

            else {

                feedback.textContent =
                    "Incorrect. " + (question.explanation || "");

            }


            card.appendChild(feedback);

        });


        card.appendChild(button);

        result.appendChild(card);

    });

}