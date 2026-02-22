/**ORDEN DE EJECUCIÓN:
 * 
 * 1. INICIALIZACIÓN (DOMContentLoaded):
 *    - Obtener referencias a elementos del DOM (input, contenedores de resultados)
 *    - Inicializar variables globales (timeout, currentPage, currentQuery)
 *    - Configurar event listener para el input de búsqueda
 * 
 * 2. FLUJO DE BÚSQUEDA (cuando el usuario escribe):
 *    a) Capturar texto del input y validar longitud mínima
 *    b) Si es válido: aplicar debounce (300ms) y ejecutar performSearch()
 *    c) Si no es válido: ocultar resultados con hideContainer()
 * 
 * 3. PROCESO DE BÚSQUEDA (performSearch):
 *    a) Mostrar estado de carga con showLoadingState()
 *    b) Realizar petición fetch al endpoint de búsqueda
 *    c) Validar respuesta (estado HTTP y tipo de contenido JSON)
 *    d) En caso de éxito: ejecutar renderResults()
 *    e) En caso de error: ejecutar showErrorState()
 * 
 * 4. RENDERIZACIÓN DE RESULTADOS (renderResults):
 *    a) Limpiar contenedores previos
 *    b) Si no hay resultados: mostrar showNoResults()
 *    c) Si hay resultados: crear elementos para cada usuario
 *    d) Si hay múltiples páginas: renderizar paginación
 *    e) Mostrar contenedor de resultados
 * 
 * 5. FUNCIONES DE UTILIDAD:
 *    - clearContainer(): Limpia contenido de elementos DOM
 *    - showContainer()/hideContainer(): Controla visibilidad del contenedor
 *    - showLoadingState(): Muestra spinner de carga
 *    - showErrorState(): Muestra mensaje de error
 *    - showNoResults(): Muestra mensaje cuando no hay coincidencias
 */

document.addEventListener('DOMContentLoaded', () => {
    
    
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const searchResultsList = document.getElementById('search-results-list');
    const searchPagination = document.getElementById('search-pagination');
    
    //Variables
    let timeout;
    let currentPage = 1;
    let currentQuery = '';
    let hasResults = false;
    
    

    //Busqueda
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        currentQuery = query;
        currentPage = 1; // Reset to first page on new search

        clearTimeout(timeout);
        if (query.length < 1) {
            hideContainer();
            return;
        }

        timeout = setTimeout(() => {
            performSearch(currentQuery, currentPage);
        }, 300); //Delay de 300ms
    });
    
    searchInput.addEventListener('focus', function() {
        if (currentQuery.length >= 1) {
            searchResults.style.display = 'block';
        }
    });

    document.addEventListener('click', function(event) {
        const isClickInsideSearch = searchInput.contains(event.target) || 
                                  searchResults.contains(event.target);
        
        if (!isClickInsideSearch) {
            searchResults.style.display = 'none';
        }
    });
    
    //Esconder Resultados
    function hideContainer() {
        searchResults.style.display = 'none';
        clearContainer(searchResultsList);
        clearContainer(searchPagination);
        hasResults = false;
    }
    function showContainer() {
        clearContainer(searchResultsList);
        clearContainer(searchPagination);
        searchResults.style.display = 'block';
    }

    //Limpiar contenedor
    function clearContainer(container) {
        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }
    }

    //Realizar Busqueda
    function performSearch(query, page) {
        
        const searchUrl = `/manager/search/?q=${encodeURIComponent(query)}&page=${page}`;
        
        fetch(searchUrl)
            .then(response => {
                // Verificar si es una respuesta exitosa
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    });
                }
                
                // Verificar que sea JSON
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    return response.text().then(text => {
                        throw new Error('La respuesta del servidor no es JSON válido');
                    });
                }
                
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                renderResults(data);
            })
            .catch(error => {
                showErrorState();
            });
    }

    

    //Mostrar estado de error
    function showErrorState() {
        clearContainer(searchResultsList);
        clearContainer(searchPagination);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'search-error';
        
        const errorText = document.createElement('p');
        errorText.textContent = 'No se encontraron resultados.';
        errorDiv.appendChild(errorText);
        searchResultsList.appendChild(errorDiv);
    }

    //Renderizar Resultados
    function renderResults(data) {
        clearContainer(searchResultsList);
        clearContainer(searchPagination);

        if (!data.users || data.users.length === 0) {
            showNoResults();
            hasResults = false;
            return
        }

        //Render
        showContainer();
        hasResults = true;
        data.users.forEach(user => {
            const link = document.createElement('a');
            link.href = `/manager/modify/${user.id}/`;
            link.textContent = user.full_name;
            
            const userDiv = document.createElement('div');
            userDiv.className = 'user-result';
            userDiv.appendChild(link);

            searchResultsList.appendChild(userDiv);
        });

    }

    //Mostrar "No hay resultados"
    function showNoResults() {
        const noResultsDiv = document.createElement('div');
        noResultsDiv.className = 'no-results';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'no-results-content';
        
        const title = document.createElement('h3');
        title.textContent = 'No se encontraron resultados';
        
        const message = document.createElement('p');
        message.textContent = 'Intenta con otros términos de búsqueda.';
        
        contentDiv.appendChild(title);
        contentDiv.appendChild(message);
        
        noResultsDiv.appendChild(contentDiv);
        searchResults.style.display = 'block'
        searchResultsList.appendChild(noResultsDiv);
    }

});