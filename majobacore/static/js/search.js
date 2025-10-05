document.addEventListener('DOMContentLoaded', () => {

    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const searchResultsList = document.getElementById('search-results-list');
    const searchPagination = document.getElementById('search-pagination');
    
    let timeout;
    let currentPage = 1;
    const currentQuery = '';
    

    //Busqueda
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        currentQuery = query;
        currentPage = 1; // Reset to first page on new search

        clearTimeout(timeout);
        if (query.length < 1) {
            hideResults();
            return;
        }

        timeout = setTimeout(() => {
            performSearch(currentQuery, currentPage);
        }, 300); //Delay de 300ms
    });

    //Esconder Resultados
    function hideResults() {
        searchResults.style.display = 'none';
        searchResultsList.innerHTML = '';
        searchPagination.innerHTML = '';
    }

    //Mostrar Resultados
    function showResults() {
        searchResults.style.display = 'block';
    }
    //Realizar Busqueda
    function performSearch(query, page) {
        fetch(`/search/?q=${encodeURIComponent(query)}&page=${page}`)
            .then(response => response.json())
            .then(data => {
                renderResults(data);
            })
            .catch(error => {console.error('Error fetching search results:', error)});
    }

    //Renderizar Resultados
    function renderResults(data) { 
        if (data.results.length === 0) {
            searchResultsList.innerHTML = 
            
        }
     }
                 
})