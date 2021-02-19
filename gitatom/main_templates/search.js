let search = (searchField) => {
  fetch('pageIndex.json')
    .then(response => response.json())
    .then(pageIndex => {
      fetch('wordIndex.json')
      .then(response => response.json())
      .then(wordIndex => {

          searchTerms = searchField.toLowerCase().split(' ')
          searchLists = []
          results = []

          searchTerms.forEach(element => { searchLists.push(wordIndex[element]) });
          // https://stackoverflow.com/questions/37320296/how-to-calculate-intersection-of-multiple-arrays-in-javascript-and-what-does-e
          // answered Aug 16 '18 at 9:57 Nina Scholz 
          pages = searchLists.reduce((a, b) => a.filter(c => b.includes(c)));
          pages.forEach(page => { results.push(pageIndex[page]) })

          div = document.querySelector('#searchResults')
          h4  = document.createElement('h4')
          h4.textContent = "Search Results"
          div.append(h4)
          results.forEach(page => {
            p = document.createElement('p')
				    a = document.createElement('a')
            a.href = page
            a.textContent = page
            p.append(a)
            div.append(p)
          })
      })
      .catch(error => {
          div = document.querySelector('#searchResults')
          p = document.createElement('p')
          p.textContent = "no results"
          div.append(p)
      })
    })
}

document.querySelector('#searchButton').onclick = function(e) {
    e.preventDefault();
    document.querySelector('#searchResults').innerHTML = ''
    search(document.querySelector('#searchField').value)}
