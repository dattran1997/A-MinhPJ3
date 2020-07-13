$( document ).ready(function() {
    console.log( "js loaded" );
    let userId = window.location.pathname.split('/')[2];
    

    $('#user-activate-btn').click( (e) => {

        $.ajax({
            url: "/update_user_status",
            type: "GET",
            contentType: "application/json",
            success: function (data,__statusCode) {
                console.log(data);
                $('#activate_modal').modal('show');
                window.location.href = `/user/${userId}`;
            },
            error: function (__xhr,__statusCode,error){
              console.log(error);
            }
        });
        
    });

    

    $('#confirm-deactivate-btn').click( (e) => {
        
        
    })
    
});
