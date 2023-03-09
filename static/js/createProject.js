$(document).ready( function(){

    // you cannot actually add or remove data to the database because 
    // the project doesn't exist yet, so add the requirements and developers to a global list
    // which gets emptied whenever you access a certain page again

    $('.add_developer').click(function(){

        let selectedId = $('#developers').find(":selected").val();
        let selectedName = $('#developers').find(":selected").text();
        let currentDevList = document.getElementById('currentdev')
    
        $.ajax({
            url: '/addDevToProjectList',
            type: 'post',
            data: {
                devId : selectedId
            },
            success:function(response){
                // remove the developer from the current list
                const node = document.createElement("li");
                node.id = selectedId;
                const textnode = document.createTextNode(selectedName);
                node.appendChild(textnode);
                currentDevList.appendChild(node);
            }
        })
    })

    $('.remove_developer').click(function(){

        let selectedId = $('#developers').find(":selected").val();
        let selectedName = $('#developers').find(":selected").text();
        let listElem = document.getElementById(selectedId)
        
        $.ajax({
            url: '/removeDevFromProjectList',
            type: 'post',
            data: {
                devId : selectedId
            },
            success:function(response){
                // add the skill to the list of current skills
                listElem.parentNode.removeChild(listElem);
            }
        })
    })

    $('.add_requirement').click(function(){

        let selectedName = $('#skillset').find(":selected").text();
        let currentReqList = document.getElementById('currentreq')
    
        $.ajax({
            url: '/addReqToProjectList',
            type: 'post',
            data: {
                reqName : selectedName
            },
            success:function(response){
                // remove the developer from the current list
                const node = document.createElement("li");
                node.id = selectedName;
                const textnode = document.createTextNode(selectedName);
                node.appendChild(textnode);
                currentReqList.appendChild(node);
            }
        })
    })

    $('.remove_requirement').click(function(){

        let selectedName = $('#skillset').find(":selected").text();
        let listElem = document.getElementById(selectedName)
        
        $.ajax({
            url: '/removeReqFromProjectList',
            type: 'post',
            data: {
                reqName : selectedName
            },
            success:function(response){
                // add the skill to the list of current skills
                listElem.parentNode.removeChild(listElem);
            }
        })
    })

})