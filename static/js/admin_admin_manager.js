$( document ).ready(function() {
    console.log( "js loaded" );
    let allAdmin = [];
    let adminID = '';
    let adminName = '';
    let adminPassword = '';

    // sub function

    const showData = (allAdmin) => {
        $('#admin-data-table').html('');

        allAdmin.map( (admin, index) => {
            console.log(admin);
            console.log(index);

            $('#admin-data-table').append(`
            <tr>
                <th scope="row">${index + 1}</th>
                <td>${admin.username}</td>
                <td>${admin.password}</td>
                <td>${admin.isAdmin ? 'admin' : 'censor'}</td>
                <td>${admin.isActive ? 'Active' : 'Deactive'}</td>
                <td>
                    <a class='edit-admin' admin_name=${admin.username} admin_id=${admin._id.$oid} class='mr-3' href='#' >edit</a> |
                    ${admin.isAdmin ? '' : `<a class='deactivate-admin' admin_id=${admin._id.$oid} href='#' >${admin.isActive ? 'Active' : 'Deactive'}</a>`}
                </td>
            </tr>
            `);

            $('.deactivate-admin').click((e) => {
                // console.log('deactivate');
                // console.log($(e.target).attr('admin_id'));
                let adminState = $(e.target).text();
                let deactivateMessage = `You really want to ${adminState} this account`
                adminID = $(e.target).attr('admin_id');
                $('#admin_deactivate_title').html(deactivateMessage);
                $('#admin_deactivate').modal('show');
            });

            $('.edit-admin').click((e) => {
                adminID = $(e.target).attr('admin_id');
                adminName = $(e.target).attr('admin_name');
                $('#admin-name').attr('placeholder', `User: ${adminName}`);
                $('#admin_edit').modal('show');
            });
        })  
    }


    // main logic

    $.ajax({
        url: "/get_all_admin",
        type: "GET",
        contentType: "application/json",
        success: function (data,__statusCode) {
            allAdmin = JSON.parse(data.allAdmin);
            // console.log(allAdmin[0]._id.$oid)
            showData(allAdmin);
        },
        error: function (__xhr,__statusCode,error){
          console.log(error);
        }
    });

    // deactivate

    $('#confirm-deactivate-btn').click((e) => {

        $.ajax({
            url: `/update_admin_status/${adminID}`,
            type: "POST",
            contentType: "application/json",
            success: function (data,__statusCode) {
                console.log(data);

                allAdmin.map((admin, index) => {
                    if (admin._id.$oid === adminID){
                        admin.isActive = !admin.isActive;
                        adminID = '';
                        console.log('change');
                        $('#admin_deactivate').modal('hide');
                    }
                });

                console.log('done');

                showData(allAdmin);

            },
            error: function (__xhr,__statusCode,error){
              console.log(error);
            }
        });
    });

    // edit

    $('#confirm-edit-btn').click((e) => {
        adminPassword = $('#admin-password').val();

        if (adminPassword === ''){
            $('#admin-password').addClass('is-invalid');
        }else{
            $.ajax({
                url: `/admin_update/${adminID}`,
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify ({
                    password: adminPassword
                }),
                success: function (data,__statusCode) {
                    console.log(data);
    
                    allAdmin.map((admin, index) => {
                        if (admin._id.$oid === adminID){
                            admin.password = adminPassword;
                            adminID = '';
                            adminPassword= '';
                            console.log('change');
                            $('#admin_edit').modal('hide');
                        }
                    });
    
                    console.log('done');
    
                    showData(allAdmin);
    
                },
                error: function (__xhr,__statusCode,error){
                  console.log(error);
                }
            });
        }
    });


    // create admin 

    $('#add-censor-btn').click((e) => {
        $('#admin_create').modal('show');
        $('#new-admin-name').removeClass('is-invalid');
        $('#nnew-admin-password').removeClass('is-invalid');
    });

    $('#confirm-create-btn').click(() => {
        adminName = $('#new-admin-name').val();
        adminPassword = $('#new-admin-password').val();
        let adminNameMessage = '';
        let adminPasswordMessage ='';



        if (adminName === ''){  
            adminNameMessage = 'Please choose a name';
            $('#new-admin-name').addClass('is-invalid');
        } else if (adminPassword == ''){
            adminPasswordMessage = 'Please choose a password';
            $('#nnew-admin-password').addClass('is-invalid');
        }else{

            $.ajax({
                url: `/admin_create`,
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify ({
                    username: adminName,
                    password: adminPassword,
                    isAdmin: false,
                    isActive:true
                }),
                success: function (data,__statusCode) {
                    console.log(data);
    
                    if (data.status === 'fail'){
                        adminNameMessage = 'User exist';
                        $('#new-admin-name').addClass('is-invalid');
                        $('#admin-name-warn').text(adminNameMessage);
                    }else if (data.status === 'success'){
                        allAdmin.push({
                            _id: JSON.parse(data.adminId),
                            username: adminName,
                            password: adminPassword,
                            isAdmin: false,
                            isActive:true
                        });
                        console.log(allAdmin);
    
                        adminName = '';
                        adminPassword= '';
                        adminNameMessage= '';
                        adminPasswordMessage= '';
                        $('#new-admin-name').removeClass('is-invalid');
                        $('#nnew-admin-password').removeClass('is-invalid');
                        $('#admin_create').modal('hide');
                    }
    
                    console.log('done');
    
                    showData(allAdmin);
    
                },
                error: function (__xhr,__statusCode,error){
                  console.log(error);
                }
            });
        }

        $('#admin-name-warn').text(adminNameMessage);
        $('#admin-password-warn').text(adminPasswordMessage);

    });


    // search 

    $('#admin-manager-search').keyup(() => {
        let keySearch = $('#admin-manager-search').val();
        let sortedAdmin = allAdmin;

        if (keySearch !== ''){
            sortedAdmin = sortedAdmin.filter((admin) => admin.username.includes(keySearch));
        }

        showData(sortedAdmin);
    });



});


