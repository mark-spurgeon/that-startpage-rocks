
/*
Slight modification for local startpage : no perfectScrollbar
*/

function showSearchPanel() {
  var p = document.getElementById('search-panel');
  p.className='searching';
  var a = document.getElementById('app-view');
  a.className='searching';
}
function hideSearchPanel() {
  var p = document.getElementById('search-panel');
  p.className='';
  var a = document.getElementById('app-view');
  a.className='';
}

function setSearchInput(query) {
  var s =document.getElementById('search-input');
  s.value = query+' ';
  searchFunction(query);
  s.focus();
}

function searchFunction(data) {
  if (data != '') {
    showSearchPanel();
    $.getJSON( "http://that.startpage.rocks/search?q="+data, function( d ) {
      $('#search-results').empty();
      var res= d.results;
      console.log('got results');
      if (d.responseType=='plugin-results') {
        $.each( res, function(k,v) {
          var a = document.createElement('a');
          if (v.type == 'image'){
            a.className='item-img';
            a.href=v.url;
            a.style.borderColor=v.brand_color;
            var img= document.createElement('div');
            img.className = 'img';
            img.style.background = "url('"+v.img+"') center center";
            img.style.backgroundSize = "contain";
            img.style.backgroundRepeat = "no-repeat";
            a.appendChild(img);
            var t = document.createElement('p');
            t.innerHTML = v.text;
            a.appendChild(t);
          } else if (v.type == 'basic') {
            a.className='item-basic';
            a.href=v.url;
            a.style.borderColor=v.brand_color;
            var t = document.createElement('p');
            t.innerHTML = v.text;
            a.appendChild(t);
          }
          $('#search-results').append(a);
        });
      } else if (d.responseType=='plugins-available') {
        var sugg_title = document.createElement('p');
        sugg_title.innerHTML = 'Search Suggestions:';
        sugg_title.className='plugins-title';
        $('#search-results').append(sugg_title);
        for (var key in res) {
          var d = document.createElement('div');
          d.className='plugin-suggestion';
          var header = document.createElement('a');
          header.className='pl-name';
          header.innerHTML=key+':';
          /*header.style.borderColor=res[key]['brand-color'];*/
          header.style.backgroundColor=res[key]['brand-color'];
          d.appendChild(header);
          for (i = 0; i < res[key]['domains'].length; i++) {
            var a = document.createElement('a');
            a.className='pl-domain';
            a.style.borderColor=res[key]['brand-color'];
            a.style.color=res[key]['brand-color'];
            a.setAttribute("onclick","setSearchInput('"+res[key]['domains'][i]+"')");
            a.innerHTML=res[key]['domains'][i];
            d.appendChild(a);
          };
          $('#search-results').append(d);
        }

      }
    })
  } else {
    hideSearchPanel()
  }
}
