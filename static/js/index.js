$( document ).ready(function() {
  console.log('js loaded');
  var post_container = [];
  var post_list = [];
  var search_key = "";

  $.ajax({
    url: "/postdata/All resources",
    type: "GET",
    success: function (data,__statusCode) {
      // console.log(JSON.parse(data));
      $(".stock-container").empty();
      let parse_data = JSON.parse(data);
      post_list = parse_data.post_list;
      post_list.reverse();
      post_list.forEach(function(post){
        // console.log(post._id.$oid);
        if(post.check == true){
          $(".stock-container").append(
            `
              <a class="card-box masonry-brick" href="/detail/${post._id.$oid}">
                <div class="card-box-overlay">
                  <p id='overlay-title'>${post.title}</p>
                </div>
                <img class="card-image" src="../static/image/${post.thumbnail}" >
              </a>
            `
          );
        }
      });
    },
    error: function (__xhr,__statusCode,error){
      console.log(error);
    }
  });

  $('.search-input').change(function(){
    search_key = $(this).val();
  });

  $('.search-button').click(function(){

    if (/^ *$/.test(search_key)){
      window.alert('input some word');
    }else {
      console.log(search_key);
      $(".stock-container").empty();
      post_list.forEach(function(post){
        // console.log(post.title);
        // console.log(post.title.toLowerCase().includes(search_key.toLowerCase()));
        if (post.title.toLowerCase().includes(search_key.toLowerCase())){
          if(post.check == true){
            $(".stock-container").append(
              `
                <a class="card-box masonry-brick" href="/detail/${post._id.$oid}">
                  <div class="card-box-overlay">
                    <p id='overlay-title'>${post.title}</p>
                  </div>
                  <img class="card-image" src="../static/image/${post.thumbnail}" >
                </a>
              `
            );
          }
        }
      });
    }
  });

  $('#logout-button').click(function() {
    window.localStorage.removeItem("username");
    window.localStorage.removeItem("id");
  });

  $('li button').click(function(){
    $('.active').removeClass( "active" );
    $(this).addClass('active');
    // console.log($(this).text());
    let type = $(this).text();
    $.ajax({
      url: `/postdata/${type}`,
      type: "GET",
      success: function (data,__statusCode) {
        // console.log(JSON.parse(data));
        $(".stock-container").empty();
        let parse_data = JSON.parse(data);
        post_list = parse_data.post_list;
        post_list.reverse();
        post_list.forEach(function(post){
          // console.log(post._id.$oid);
          if(post.check == true){
            $(".stock-container").append(
              `
                <a class="card-box masonry-brick" href="/detail/${post._id.$oid}">
                  <div class="card-box-overlay">
                    <p id='overlay-title'>${post.title}</p>
                  </div>
                  <img class="card-image" src="../static/image/${post.thumbnail}" >
                </a>
              `
            );
          }
          
        });
      },
      error: function (__xhr,__statusCode,error){
        console.log(error);
      }
    });
  });



});
