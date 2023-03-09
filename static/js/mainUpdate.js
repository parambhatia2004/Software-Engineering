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

})