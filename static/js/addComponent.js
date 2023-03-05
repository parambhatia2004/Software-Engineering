
const addBtn = document.querySelector(".add");

const input = document.querySelector(".estimations")

function removeInput(){
    $.ajax({
        url: '/removeCostComponent',
        type: 'post',
        data: {
            projectID : document.getElementById("projectid").value(),
            name : this.parentElement.childNodes[0].value(),
            //use this as id of component for this project
            absval: this.parentElement.childNodes[1].value(),
            worst: this.parentElement.childNodes[2].value(),
            best: this.parentElement.childNodes[3].value(),
            average: this.parentElement.childNodes[4].value()
        },
        success:function(response){
            // ajax processing of data
            this.parentElement.remove();
        }
    })
   
}

function submitInput(){
    $.ajax({
        url: '/submitCostComponent',
        type: 'post',
        data: {
            projectID : document.getElementById("projectid").value(),
            name : this.parentElement.childNodes[0].value(),
            //use this as id of component for this project
            absval: this.parentElement.childNodes[1].value(),
            worst: this.parentElement.childNodes[2].value(),
            best: this.parentElement.childNodes[3].value(),
            average: this.parentElement.childNodes[4].value()
        },
        success:function(response){
        }
    }) 
}

function addInput(){
    const name = document.createElement("input");
    name.type="text"
    name.placeholder="Name of the component"

    const absval = document.createElement("input");
    absval.type="number"
    absval.placeholder="Absolute value"

    const worst = document.createElement("input");
    worst.type="number"
    worst.placeholder="Worst case estimation"

    const best = document.createElement("input");
    best.type="number"
    best.placeholder="Best case estimation"

    const average = document.createElement("input");
    average.type="number"
    average.placeholder="Average estimation"

    const btn = document.createElement("a");
    btn.className = "delete";
    btn.innerHTML = "&times";
    btn.addEventListener("click", removeInput)

    const submit = document.createElement("input");
    submit.type="submit";
    submit.className = "submit";
    submit.name = "Submit";
    submit.addEventListener("submit", submitInput)
   

    const flex = document.createElement("div");
    flex.className="flex"

    const hr = document.createElement("hr")
    hr.className="customHR"

    input.appendChild(flex)
    flex.appendChild(name);
    flex.appendChild(absval);
    flex.appendChild(worst);
    flex.appendChild(best);
    flex.appendChild(average);
    flex.appendChild(btn);
    flex.appendChild(submit);
    flex.appendChild(hr);
}

addBtn.addEventListener("click", addInput);