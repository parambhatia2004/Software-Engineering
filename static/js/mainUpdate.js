$(document).ready( function(){

    $('#changeDescription').click(function(){

        let changedDesc = $('#newDescription').val();
        console.log(changedDesc);
       
        $.ajax({
            url: '/changeDescription',
            type: 'post',
            data: {
                description : changedDesc
            },
            success:function(response){
            }
        })
    })

    $('#changeStatus').click(function(){

        let selectedName = $('#statusSelect').find(":selected").text();
        $.ajax({
            url: '/changeStatus',
            type: 'post',
            data: {
                status : selectedName
            },
            success:function(response){
            }
        })
    })

    $('#submitDevelopers').click(function(){
        // data is already in the backend session
        $.ajax({
            url: '/updateDevelopers',
            type: 'post',
            data: { },
            success:function(response){
            }
        })
    })

    $('#submitRequiements').click(function(){
         // data is already in the backend session
        $.ajax({
            url: '/updateRequirements',
            type: 'post',
            data: { },
            success:function(response){
            }
        })
    })


})