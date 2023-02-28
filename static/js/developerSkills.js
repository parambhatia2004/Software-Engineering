$(document).ready( function(){

    $('.add_skill').click(function(){
        console.log('add skill clicked')

        let selectedName = $('#skillSelect').find(":selected").text()
        let currentSkillList = document.getElementById('currentskills')
        if(currentSkillList == null){
            console.log('current skill list is null')
            const newList = document.createElement("ul");
            li = document.createElement("li");
            newList.id = 'currentskills';
            li.id = selectedName;
            const textnode = document.createTextNode(selectedName);
            li.appendChild(textnode);
            newList.appendChild(li);
        }
        currentSkillList = document.getElementById('currentskills')
    
        $.ajax({
            url: '/addDeveloperSkill',
            type: 'post',
            data: {
                skillName : selectedName
            },
            success:function(response){
                // add the skill to the list of current skills
                const node = document.createElement("li");
                node.id = selectedName;
                const textnode = document.createTextNode(selectedName);
                node.appendChild(textnode);
                currentSkillList.appendChild(node);
            }
        })
    })

    $('.remove_skill').click(function(){

        let selectedName = $('#skillSelect').find(":selected").text()
        let listElem = document.getElementById(selectedName)
    
        $.ajax({
            url: '/removeDeveloperSkill',
            type: 'post',
            data: {
                skillName : selectedName
            },
            success:function(response){
                // add the skill to the list of current skills
                listElem.parentNode.removeChild(listElem);
            }
        })
    })

})