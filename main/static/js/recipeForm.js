// Script managing dynamic adding/removing formset rows.
// Second functionality is to modify new formset queryset
// to exclude already chosen ingredients.
// Corresponding views: update_session and update_options.
function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
    }
    function cloneMore(selector, prefix) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    newElement.find(':input:not([type=button]):not([type=submit]):not([type=reset])').each(function() {
        let name = $(this).attr('name')
        if (name) {
        name = name.replace('-' + (total - 1) + '-', '-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    }
    });
    newElement.find('label').each(function() {
        var forValue = $(this).attr('for');
        if (forValue) {
          forValue = forValue.replace('-' + (total-1) + '-', '-' + total + '-');
          $(this).attr({'for': forValue});
        }
    });
    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
    var conditionRow = $('.form-row:not(:last)');
    conditionRow.find('.btn.add-form-row')
    .removeClass('btn-success').addClass('btn-danger')
    .removeClass('add-form-row').addClass('remove-form-row')
    .html('<span class="glyphicon glyphicon-minus" aria-hidden="true">-</span>');
    return false;
    }
    function deleteForm(prefix, btn) {
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (total > 1){
        btn.closest('.form-row').remove();
        var forms = $('.form-row');
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        for (var i=0, formCount=forms.length; i<formCount; i++) {
            $(forms.get(i)).find(':input').each(function() {
                updateElementIndex(this, prefix, i);
            });
        }
    }
    return false;
    }
    $(document).on('click', '.add-form-row', function(e){
    e.preventDefault();
    cloneMore('.form-row:last', 'form');
    return false;
    });
    $(document).on('click', '.remove-form-row', function(e){
    e.preventDefault();
    deleteForm('form', $(this));
    return false;
    });


function updateSession() {
        var fields = $( ":input" ).serializeArray();
        let updateING = '';
        jQuery.each( fields, function( i, field ) {
            if(i>5 && i!=(fields.length-1) && field.value!='' && isNaN(field.value)){
                updateING = updateING + "#" + field.value;
                console.log(updateING);
            }
        });
        var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();

        function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                // if not safe, set csrftoken
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        $.ajax({
            headers: {'X-CSRFToken': csrftoken},
            type: "POST",
            url: '/updateSS/',
            data: {'ingredients': updateING},
            success: function(data){
                                    console.log(data)
                                    },
            error: function(error_data){
                                        console.log(error_data)
                                        }
        })

      }

      function updateOptionss(){
        $.get('/updateOP/', function(data){
                                    $('select:last').html(data)
                                    } );
      }


      function updateOptions(){
      var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();

        function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                // if not safe, set csrftoken
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        $.ajax({
            headers: {'X-CSRFToken': csrftoken},
            type: "GET",
            url: '/updateOP/',
            data: {},
            success: function(data){
                                    $('select:last').html(data)
                                    console.log(data)
                                    },
            error: function(error_data){
                                        console.log(error_data)
                                        }
        })
      }
      $( "select" ).change( updateSession );
      $(document).on('click', '.remove-form-row', updateSession);
      updateSession();
      $(document).on('click', '.add-form-row', updateOptions);
      $(document).on('click', '.remove-form-row', updateOptions);