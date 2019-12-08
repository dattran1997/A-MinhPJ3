$( document ).ready(function() {
    console.log( "js loaded" );
    let username = "";
    let password = "";

    $('.login-form').change(function(){
      username = $('#username').val();
      password = $('#password').val();
    });

    $('.login-form').submit(function(e){
      e.preventDefault();

      $.ajax({
        url: "/admin_login",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify ({
          username: username,
          password: password
        }),
        success: function (data,__statusCode) {
          console.log(data);
          $('#userwarn').text(" ");
          $('#passwarn').text(" ");

          if (data.userwarn){
            $('#userwarn').text(data.userwarn);
          }else if (data.passwarn){
            $('#passwarn').text(data.passwarn);
          }else{
            window.localStorage.setItem('username', data.username );
            window.localStorage.setItem('id', data.id);
            window.location.href = "/admin_page/waiting";
          }
        },
        error: function (__xhr,__statusCode,error){
          console.log(error);
        }
      });
    });

});