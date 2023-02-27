$(document).ready( function(){

    $('.add_skill').click(function(){

        let selectedName = $('#skillSelect').find(":selected").text()
        let currentSkillList = document.getElementById('#currentSkills')
    
        $.ajax({
            url: '/addDeveloperSkill',
            type: 'post',
            data: {
                skillName : selectedName
            },
            success:function(response){
                // add the skill to the list of current skills
                const node = document.createElement("li");
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