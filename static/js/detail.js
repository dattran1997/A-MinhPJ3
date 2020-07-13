console.log('js loaded');
let postId = window.location.pathname.split('/')[2];


$( document ).ready(function() {
    let allMessages = [];
    var message = '';

    // sub function

    let showAllMessage = (allMessages) => {
      $('#comment-container').html('');

      allMessages.map((message) => {
        $('#comment-container').append(`
          <div class="comment">
            ${message.content}
            <div class="text-right"><a class='author-comment' href="/user/${message.userid}">- by ${message.username} -</a></div>
          </div>
        `);
      });
    }

    let getAllMessage = () => {

      $.ajax({
        url: `/get_all_messages/${postId}`,
        type: "GET",
        success: function (data,__statusCode) {
          // console.log(JSON.parse(data.all_comments));
          allMessages = JSON.parse(data.all_comments);
          allMessages.reverse();

          showAllMessage(allMessages);
        },
        error: function (__xhr,__statusCode,error){
          console.log(error);
        }
      });
    }

    // main js logic

    getAllMessage();


    $('#comment-input').change(function(){
        message = $('#comment-input').val();

        console.log(message);

        $.ajax({
            url: `/post_message`,
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify ({
              message: message,
              postId: postId,
            }),
            success: function (data,__statusCode) {
              console.log(data.comment);
              allMessages.unshift(data.comment)

              showAllMessage(allMessages);
            //   reset input data  
              $('#comment-input').val('');
              message = '';  
            },
            error: function (__xhr,__statusCode,error){
              console.log(error);
            }
          });
    });

});