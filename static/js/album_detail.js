$(document).ready(() => {
    console.log('js loaded');
    let albumId = window.location.pathname.split('/')[2];
    let userId = window.location.pathname.split('/')[3];
    let allAlbumPosts = [];
    let allSuggestPost = [];
    let albumName = '';
    console.log(userId);
    $('.delete-post-btn').hide();

    // sub function
    let showData = (allAlbumPost) => {
        $('#post-item-container').html('');
        $('#post-suggest-container').html('');

        if (allAlbumPost.length <= 0){
            $('#post-item-container').append('<h3 class="text-center py-3 w-100">No post in the collection</h3>')
        }else{
            allAlbumPost.map((post) => {
                $('#post-item-container').append(`
                    <div class='post-item-wrap'>
                        <a href="/detail/${post._id.$oid}">
                            <div class="post-item">
                                <div class="overlay">
                                    
                                    <p class="overlay-title">${post.title}</p>
                                </div>
                                <img src="/static/image/${post.thumbnail}" alt="">
                            </div>
                        </a>
                        <button post-id='${post._id.$oid}' class="delete-post-btn btn btn-primary m-3 float-right">-</button>
                    </div>
                `);

                $('.delete-post-btn').click((e) => {
                    let postId = $(e.target).attr('post-id');
                    $.ajax({
                        url: `/remove_album_post`,
                        type: "POST",
                        contentType: "application/json",
                        data: JSON.stringify ({
                            albumId: albumId,
                            postId: postId,    
                        }),
                        success: function (data,__statusCode) {
                            console.log(data);
                            allAlbumPosts = allAlbumPost.filter((post) => post._id.$oid != postId);
                            console.log(allAlbumPosts);
                            showData(allAlbumPosts);
                        },
                        error: function (__xhr,__statusCode,error){
                          console.log(error);
                        }
                    });
                });
            });
        }

        showSuggestData();
    }

    let showSuggestData = () => {
        $('#post-suggest-container').html('');
        $('#post-suggest-container').append('<p id="post-suggest-title" class="text-center d-block w-100">choose one of your post</p>');        

        $.ajax({
            url: `/get_album_suggest/${userId}`,
            type: "GET",
            contentType: "application/json",
            success: function (data,__statusCode) {
                console.log(JSON.parse(data.suggestPost));
                allSuggestPost = JSON.parse(data.suggestPost);
                // let allSuggestPostFilter = allSuggestPost.reduce((filtered, post) => {
                //     if(allAlbumPosts.length > 0){
                //         if( allAlbumPosts.map((albumPost) => albumPost._id.$oid).indexOf(post._id.$oid) === -1 ){
                //             filtered.push(post);
                //         }
                //     }else{
                //         filtered = allSuggestPost
                //     }
                    
                //     return filtered;
                // }, []);

                // let allSuggestPostFilter1 = allSuggestPost.filter((post) => allAlbumPosts.map((albumPost) => albumPost._id.$oid).indexOf(post._id.$oid) == -1);

                // allSuggestPost = allSuggestPostFilter1;

                console.log(allSuggestPost);

                allSuggestPost.map((post) => {
                    $('#post-suggest-container').append(`
                        <a>
                            <div class="post-item">
                                <div class="overlay">
                                    <button post-id='${post._id.$oid}' class="add-post-btn btn btn-primary m-3 float-right">+</button>
                                    <p class="overlay-title">${post.title}</p>
                                </div>
                                <img src="/static/image/${post.thumbnail}" alt="">
                            </div>
                        </a>
                    `);

                    $('.add-post-btn').click((e) => {

                        console.log('click');
                        let postId = $(e.target).attr('post-id');
                        $.ajax({
                            url: `/add_album_post`,
                            type: "POST",
                            contentType: "application/json",
                            data: JSON.stringify ({
                                albumId: albumId,
                                postId: postId,    
                            }),
                            success: function (data,__statusCode) {
                                console.log(data);
                                console.log(allAlbumPosts);
                                let addedPost = allSuggestPost.filter((post) => post._id.$oid === postId);
                                console.log(addedPost);
                                allAlbumPosts.push(addedPost[0]);
                                console.log(allAlbumPosts);
                                showData(allAlbumPosts);
                            },
                            error: function (__xhr,__statusCode,error){
                              console.log(error);
                            }
                        });
                    });
                })
            },
            error: function (__xhr,__statusCode,error){
              console.log(error);
            }
        });
    }

    // main logic
    $.ajax({
        url: `/get_album_detail/${albumId}`,
        type: "GET",
        contentType: "application/json",
        success: function (data,__statusCode) {
            console.log(JSON.parse(data.postList));
            allAlbumPosts = JSON.parse(data.postList);
            albumName = data.albumName;
            showData(allAlbumPosts);

            $('#album-name').text(albumName);
        },
        error: function (__xhr,__statusCode,error){
          console.log(error);
        }
    });

    

    // // add post 

});