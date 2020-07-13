$( document ).ready(function() {
    console.log( "js loaded" );
    let userId = window.location.pathname.split('/')[2];
    $('#album-btn').attr("href",`/album/${userId}`);

    $('#user-deactivate-btn').click( (e) => {
        $('#deactivate_modal').modal('show');
    });

    $('#confirm-deactivate-btn').click((e) => {
        
        $.ajax({
            url: "/update_user_status",
            type: "GET",
            contentType: "application/json",
            success: function (data,__statusCode) {
              console.log(data);
              location.reload();
            },
            error: function (__xhr,__statusCode,error){
              console.log(error);
            }
        });
    })
    
});
