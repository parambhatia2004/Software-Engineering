
const addBtns = document.getElementsByClassName("add");

function removeInput(){
    var element = this;
    eType = element.parentNode.querySelector('input[name="type"]').value;
    eName = element.parentNode.querySelector('input[name="name"]').value;
    eWorst = element.parentNode.querySelector('input[name="worst"]').value;
    eBest = element.parentNode.querySelector('input[name="best"]').value;
    eAbsVal = element.parentNode.querySelector('input[name="absval"]').value;
    eAverage = element.parentNode.querySelector('input[name="average"]').value;
    if(element.parentElement.hasChildNodes()){
        $.ajax({
            url: '/removeCostComponent',
            type: 'post',
            data: {
                projectID : document.getElementById("projectriskid").value,
                type : eType,
                name : eName,
                //use this as id of component for this project
                absval: eAbsVal,
                worst: eWorst,
                best: eBest,
                average: eAverage
            },
            success:function(response){
                // ajax processing of data
                console.log("removal success")
                element.parentElement.remove();
            }
        }) 
    }
}

function submitInput(){
    var element = this;
    eType = element.parentNode.querySelector('input[name="type"]').value;
    eName = element.parentNode.querySelector('input[name="name"]').value;
    eWorst = element.parentNode.querySelector('input[name="worst"]').value;
    eBest = element.parentNode.querySelector('input[name="best"]').value;
    eAbsVal = element.parentNode.querySelector('input[name="absval"]').value;
    eAverage = element.parentNode.querySelector('input[name="average"]').value;
    var check = !((eName === "") || (eWorst === "") || (eBest === "") || (eAverage === ""))
    if(element.parentElement.hasChildNodes()&&check){
        $.ajax({
            url: '/submitCostComponent',
            type: 'post',
            data: {
                projectID : document.getElementById("projectriskid").value,
                type : eType,
                name : eName,
                //use this as id of component for this project
                absval: eAbsVal,
                worst: eWorst,
                best: eBest,
                average: eAverage
            },
            success: function(response){
                console.log("success")
                element.parentElement.childNodes[7].remove()
            },
            error: function(response){
                console.log("error")
                element.parentElement.remove();
            }
        }) 
    }
    
}

function addInput(item){
    const name = document.createElement("input");
    name.type="text"
    name.name="name"
    name.placeholder="Name of the component"

    const absval = document.createElement("input");
    absval.type="number"
    absval.name="absval"
    absval.placeholder="Absolute value (optional)"

    const worst = document.createElement("input");
    worst.type="number"
    worst.name="worst"
    worst.placeholder="Worst case estimation"

    const best = document.createElement("input");
    best.type="number"
    best.name="best"
    best.placeholder="Best case estimation"

    const average = document.createElement("input");
    average.type="number"
    average.name="average"
    average.placeholder="Average estimation"

    const btn = document.createElement("a");
    btn.className = "delete";
    btn.innerHTML = "&times";
    btn.addEventListener("click", removeInput)

    const submit = document.createElement("input");
    submit.type="button";
    submit.className = "submit";
    submit.value = "Submit";
    submit.addEventListener("click", submitInput)
   

    const flex = document.createElement("div");
    flex.className="flex"

    const hr = document.createElement("hr")
    hr.className="customHR"

    const budget = document.createElement("input")
    budget.type ="hidden"
    budget.name="type"
    budget.value="Cost"

    const time = document.createElement("input")
    time.type ="hidden"
    time.name="type"
    time.value="Time"

    var input
    if(item===1){
        input = document.querySelector("#timeEstimation");
    } else {
        input = document.querySelector("#budgetEstimation")
    }

    input.appendChild(flex)
    if (input.id === "budgetEstimation"){
        console.log(input.id);
        flex.appendChild(budget)
    } else {
        flex.appendChild(time)
    }
    flex.appendChild(name);
    flex.appendChild(absval);
    flex.appendChild(worst);
    flex.appendChild(best);
    flex.appendChild(average);
    flex.appendChild(btn);
    flex.appendChild(submit);
    flex.appendChild(hr);
}

var deleteBtns = document.getElementsByClassName("delete")
for(var i=0; i<deleteBtns.length; i++){
    var item = deleteBtns[i];
    item.addEventListener("click", removeInput)
}
var count = addBtns.length;

for(var i = 0; i < count; i++) {
    var item = addBtns[i];
    const index = i;
    item.addEventListener("click", function(){addInput(index)});
}