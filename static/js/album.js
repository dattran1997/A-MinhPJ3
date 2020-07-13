$(document).ready( function() {
    console.log('js loaded');
    let albumName ='';
    let allAlbums = [];
    let userId = window.location.pathname.split('/')[2];
    console.log(userId);
    let albumId = '';
    let albumTitle ='';

    // sub function

    $(document).on("click", "a.rename-album-btn", function() {
        $('#album-title').val(albumTitle);
        $('#album_rename').modal('show');
    });

    $('#album-title').keyup(() => {
        albumTitle = $('#album-title').val(); 
    });

    $('#confirm-rename-album').click(() => {

        $.ajax({
            url: `/album_update`,
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify ({
                albumId: albumId,  
                title: albumTitle, 
            }),
            success: function (data,__statusCode) {
                console.log(data);
                allAlbums.map((album) => {
                    if(album._id.$oid === albumId){
                        album.title = albumTitle
                    }
                })

                $('#album_rename').modal('hide');

                showData(allAlbums);
            },
            error: function (__xhr,__statusCode,error) {
              console.log(error);
            }
        });
    });


    $(document).on("click", "a.delete-album-btn", function() {

        $.ajax({
            url: `/album_delete`,
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify ({
                albumId: albumId,     
            }),
            success: function (data,__statusCode) {
                console.log(data);
                allAlbums = allAlbums.filter((value) => value._id.$oid !== albumId );

                showData(allAlbums);
            },
            error: function (__xhr,__statusCode,error) {
              console.log(error);
            }
        });
    });
    

    let showData = (allAlbums) => {
        $('#collection-item-container').html('');
        allAlbums.map((album) => {
            $('#collection-item-container').append(`
                <div class="collection-item">
                    <a href='/album_detail/${album._id.$oid}/${userId}'>
                        <img src=${album.thumbnail} alt="">
                    </a>
                    <div class="collection-item-detail">
                        <div>
                            <b class="title">${album.title}</b>
                            <button id='${album._id.$oid}' type="button" class="btn btn-light myPopover float-right text-primary"
                                style='padding: 2px 10px;'
                                data-toggle="popover"
                                data-placement="bottom"
                                data-html="true"
                                data-trigger="focus"
                                data-popover-content="#album-edit-menu-popover">
                                <i id='${album._id.$oid}' class="fas fa-ellipsis-v"></i>
                            </button>

                            <div id='album-edit-menu-popover' style="display: none;">
                                <a id='${album._id.$oid}' class="d-block rename-album-btn" onclick='renameClick(${album._id.$oid})' href="#">rename</a>
                                <a id='${album._id.$oid}' class="d-block delete-album-btn" href="#">delete</a>
                            </div>
                
                        </div>
                        <p class="detail">${album.postId.length} posts | Created by <b>${album.userId.username}</b></p>
                    </div>
                </div>
            `);

            // popover event

            $(".myPopover").popover({
                html : true,
                content: function() {
                    var elementId = $(this).attr("data-popover-content");
                    return $(elementId).html();
                }
    
            });

            $('.myPopover').click((event) => {
                albumTitle = $(event.target).parent().find('.title').html();
                console.log($(event.target).parent().find('.title').html());
                albumId = $(event.target).attr("id");
                console.log(albumId);
            });

            $('.myPopover i').click((event) => {
                event.stopPropagation();
                console.log($(event.target).parent().parent().find('.title').html());
                albumTitle = $(event.target).parent().parent().find('.title').html();
                albumId = $(event.target).attr("id");
                console.log(albumId);
            });

            // delete album

        });    
       
    }

    // main logic

    $.ajax({
        url: `/albums/${userId}`,
        type: "GET",
        contentType: "application/json",
        success: function (data,__statusCode) {
            console.log(JSON.parse(data.all_admin));
            allAlbums = JSON.parse(data.all_admin);
            showData(allAlbums);
        },
        error: function (__xhr,__statusCode,error){
          console.log(error);
        }
    });


    // create album

    $('#add-collection-btn').click(() => {
        $('#album_create').modal('show');
        $('#album_name').removeClass('is-invalid');
        $('#album_name').val('');
    });

    $('#confirm-add-collection').click(() => {

        albumName = $('#album_name').val();
        if ( albumName === ''){
            $('#album_name').addClass('is-invalid');
        }else{

            $.ajax({
                url: `/album_create`,
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify ({
                    title: albumName,     
                }),
                success: function (data,__statusCode) {
                    console.log(data);
                    allAlbums.push({
                        _id: JSON.parse(data.newAlbumID),
                        ...JSON.parse(data.albumDetail),
                    })
                    showData(allAlbums);

                    console.log(allAlbums);

                    $('#album_create').modal('hide');
                },
                error: function (__xhr,__statusCode,error){
                  console.log(error);
                }
            });
        }


    });

});