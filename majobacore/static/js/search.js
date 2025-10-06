document.addEventListener('DOMContentLoaded', () => {
    console.log('=== INICIALIZANDO SISTEMA DE BÚSQUEDA ===');
    console.log('DOM completamente cargado');

    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const searchResultsList = document.getElementById('search-results-list');
    const searchPagination = document.getElementById('search-pagination');
    
    console.log('Elementos del DOM encontrados:');
    console.log('- searchInput:', searchInput);
    console.log('- searchResults:', searchResults);
    console.log('- searchResultsList:', searchResultsList);
    console.log('- searchPagination:', searchPagination);
    
    // Verificar que todos los elementos existen
    if (!searchInput) {
        console.error('ERROR: No se encontró el elemento #search-input');
        return;
    }
    if (!searchResults) {
        console.error('ERROR: No se encontró el elemento #search-results');
        return;
    }
    if (!searchResultsList) {
        console.error('ERROR: No se encontró el elemento #search-results-list');
        return;
    }
    if (!searchPagination) {
        console.error('ERROR: No se encontró el elemento #search-pagination');
        return;
    }
    
    console.log('Todos los elementos DOM están disponibles');
    
    let timeout;
    let currentPage = 1;
    let currentQuery = '';
    
    console.log('Variables inicializadas:', { timeout, currentPage, currentQuery });

    //Busqueda
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        currentQuery = query;
        currentPage = 1; // Reset to first page on new search
        
        console.log('=== INPUT DETECTADO ===');
        console.log('Query actual:', query);
        console.log('Longitud del query:', query.length);

        clearTimeout(timeout);
        if (query.length < 1) {
            console.log('Query muy corto, ocultando resultados');
            hideResults();
            return;
        }

        console.log('Configurando timeout de 300ms...');
        timeout = setTimeout(() => {
            console.log('Timeout ejecutado, iniciando búsqueda...');
            performSearch(currentQuery, currentPage);
        }, 300); //Delay de 300ms
    });
    
    console.log('Event listener agregado al input de búsqueda');
    console.log('=== SISTEMA DE BÚSQUEDA INICIALIZADO ===');

    //Esconder Resultados
    function hideResults() {
        searchResults.style.display = 'none';
        clearContainer(searchResultsList);
        clearContainer(searchPagination);
    }

    //Limpiar contenedor
    function clearContainer(container) {
        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }
    }

    //Mostrar Resultados
    function showResults() {
        searchResults.style.display = 'block';
    }
    //Realizar Busqueda
    function performSearch(query, page) {
        console.log('=== INICIO BÚSQUEDA FRONTEND ===');
        console.log('Query:', query);
        console.log('Page:', page);
        console.log('Current URL:', window.location.href);
        
        // Mostrar estado de carga
        showLoadingState();
        
        const searchUrl = `/manager/search/?q=${encodeURIComponent(query)}&page=${page}`;
        console.log('URL de búsqueda:', searchUrl);
        console.log('Query codificada:', encodeURIComponent(query));
        
        console.log('Iniciando fetch...');
        fetch(searchUrl)
            .then(response => {
                console.log('=== RESPUESTA RECIBIDA ===');
                console.log('Status:', response.status);
                console.log('Status Text:', response.statusText);
                console.log('OK:', response.ok);
                console.log('Headers:', [...response.headers.entries()]);
                console.log('Content-Type:', response.headers.get('content-type'));
                console.log('URL final:', response.url);
                
                // Verificar si es una respuesta exitosa
                if (!response.ok) {
                    console.error('Respuesta no exitosa, obteniendo texto...');
                    return response.text().then(text => {
                        console.error('Contenido de respuesta de error:');
                        console.error(text.substring(0, 500) + '...');
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    });
                }
                
                // Verificar que sea JSON
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    console.error('La respuesta no es JSON, obteniendo contenido...');
                    return response.text().then(text => {
                        console.error('Contenido recibido (no-JSON):');
                        console.error(text.substring(0, 500) + '...');
                        throw new Error('La respuesta del servidor no es JSON válido');
                    });
                }
                
                console.log('Parseando JSON...');
                return response.json();
            })
            .then(data => {
                console.log('=== DATOS JSON RECIBIDOS ===');
                console.log('Datos completos:', data);
                console.log('Número de resultados:', data.results ? data.results.length : 'No definido');
                console.log('Total de resultados:', data.total_results);
                console.log('Página actual:', data.current_page);
                console.log('Total de páginas:', data.total_pages);
                console.log('Tiene anterior:', data.has_previous);
                console.log('Tiene siguiente:', data.has_next);
                
                if (data.error) {
                    console.error('Error en datos JSON:', data.error);
                    if (data.details) {
                        console.error('Detalles del error:', data.details);
                    }
                    throw new Error(data.error);
                }
                
                console.log('Llamando a renderResults...');
                renderResults(data);
                console.log('=== BÚSQUEDA COMPLETADA ===');
            })
            .catch(error => {
                console.error('=== ERROR EN BÚSQUEDA ===');
                console.error('Tipo de error:', error.constructor.name);
                console.error('Mensaje de error:', error.message);
                console.error('Stack trace:', error.stack);
                console.error('Error completo:', error);
                showErrorState();
            });
    }

    //Mostrar estado de carga
    function showLoadingState() {
        clearContainer(searchResultsList);
        
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'search-loading';
        
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        
        const loadingText = document.createElement('p');
        loadingText.textContent = 'Buscando...';
        
        loadingDiv.appendChild(spinner);
        loadingDiv.appendChild(loadingText);
        searchResultsList.appendChild(loadingDiv);
        
        showResults();
    }

    //Mostrar estado de error
    function showErrorState() {
        clearContainer(searchResultsList);
        clearContainer(searchPagination);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'search-error';
        
        const errorIcon = document.createElement('i');
        errorIcon.className = 'fas fa-exclamation-triangle';
        
        const errorText = document.createElement('p');
        errorText.textContent = 'Error al realizar la búsqueda. Intenta nuevamente.';
        
        errorDiv.appendChild(errorIcon);
        errorDiv.appendChild(errorText);
        searchResultsList.appendChild(errorDiv);
    }

    //Renderizar Resultados
    function renderResults(data) {
        console.log('=== INICIO RENDERIZADO ===');
        console.log('Datos recibidos para renderizar:', data);
        console.log('Tipo de datos:', typeof data);
        console.log('Es array data.results?:', Array.isArray(data.results));
        console.log('Longitud de resultados:', data.results ? data.results.length : 'undefined');
        
        // Limpiar contenedores
        console.log('Limpiando contenedores...');
        clearContainer(searchResultsList);
        clearContainer(searchPagination);

        if (!data.results || data.results.length === 0) {
            console.log('No hay resultados, mostrando mensaje...');
            showNoResults();
            showResults();
            return;
        }

        console.log('Hay resultados, procesando...');
        
        // Mostrar información de resultados
        console.log('Agregando información de resultados...');
        appendResultsInfo(data);

        // Renderizar cada resultado
        console.log('Renderizando cada resultado...');
        data.results.forEach((result, index) => {
            console.log(`Procesando resultado ${index + 1}:`, result);
            const resultElement = createResultElement(result);
            console.log(`Elemento creado para resultado ${index + 1}:`, resultElement);
            searchResultsList.appendChild(resultElement);
        });

        // Renderizar paginación si hay múltiples páginas
        if (data.total_pages > 1) {
            console.log('Renderizando paginación...');
            renderPagination(data);
        } else {
            console.log('No se necesita paginación (solo 1 página)');
        }

        console.log('Mostrando resultados...');
        showResults();
        console.log('=== RENDERIZADO COMPLETADO ===');
    }

    //Mostrar "No hay resultados"
    function showNoResults() {
        const noResultsDiv = document.createElement('div');
        noResultsDiv.className = 'no-results';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'no-results-content';
        
        const icon = document.createElement('i');
        icon.className = 'fas fa-search';
        
        const title = document.createElement('h3');
        title.textContent = 'No se encontraron resultados';
        
        const message = document.createElement('p');
        message.innerHTML = `No hay coincidencias para "<strong>${currentQuery}</strong>"`;
        
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'search-suggestions';
        
        const suggestionsTitle = document.createElement('p');
        suggestionsTitle.textContent = 'Sugerencias:';
        
        const suggestionsList = document.createElement('ul');
        
        const suggestions = [
            'Verifica la ortografía',
            'Intenta con términos más generales',
            'Usa palabras clave diferentes'
        ];
        
        suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.textContent = suggestion;
            suggestionsList.appendChild(li);
        });
        
        suggestionsDiv.appendChild(suggestionsTitle);
        suggestionsDiv.appendChild(suggestionsList);
        
        contentDiv.appendChild(icon);
        contentDiv.appendChild(title);
        contentDiv.appendChild(message);
        contentDiv.appendChild(suggestionsDiv);
        
        noResultsDiv.appendChild(contentDiv);
        searchResultsList.appendChild(noResultsDiv);
    }

    //Agregar información de resultados
    function appendResultsInfo(data) {
        const infoDiv = document.createElement('div');
        infoDiv.className = 'results-info';
        
        const resultText = document.createElement('p');
        resultText.innerHTML = `Se encontraron <strong>${data.total_results}</strong> resultado(s) para "<strong>${currentQuery}</strong>"`;
        
        const pageInfo = document.createElement('small');
        pageInfo.textContent = `Página ${data.current_page} de ${data.total_pages}`;
        
        infoDiv.appendChild(resultText);
        infoDiv.appendChild(pageInfo);
        searchResultsList.appendChild(infoDiv);

    }

    //Crear elemento de resultado
    function createResultElement(result) {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'search-result-item';
        
        // Crear contenido según el tipo
        const contentDiv = createResultContent(result);
        resultDiv.appendChild(contentDiv);
        
        // Agregar evento click
        resultDiv.addEventListener('click', () => {
            handleResultClick(result, resultDiv);
        });
        
        return resultDiv;
    }

    //Crear contenido del resultado
    function createResultContent(result) {
        const contentDiv = document.createElement('div');
        contentDiv.className = 'result-content';
        
        // Header del resultado
        const headerDiv = createResultHeader(result);
        contentDiv.appendChild(headerDiv);
        
        // Detalles del resultado
        const detailsDiv = createResultDetails(result);
        contentDiv.appendChild(detailsDiv);
        
        // Acciones del resultado
        const actionsDiv = createResultActions(result);
        contentDiv.appendChild(actionsDiv);
        
        return contentDiv;
    }

    //Crear header del resultado
    function createResultHeader(result) {
        const headerDiv = document.createElement('div');
        headerDiv.className = 'result-header';
        
        // Avatar
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'result-avatar';
        const avatarIcon = document.createElement('i');
        
        // Determinar icono según tipo
        switch(result.type) {
            case 'user':
                avatarIcon.className = 'fas fa-user';
                break;
            case 'project':
                avatarIcon.className = 'fas fa-project-diagram';
                break;
            case 'manager':
                avatarIcon.className = 'fas fa-user-tie';
                break;
            default:
                avatarIcon.className = 'fas fa-file';
        }
        
        avatarDiv.appendChild(avatarIcon);
        
        // Información
        const infoDiv = document.createElement('div');
        infoDiv.className = 'result-info';
        
        const title = document.createElement('h4');
        title.textContent = result.title;
        
        const subtitle = document.createElement('p');
        subtitle.className = 'result-subtitle';
        subtitle.textContent = result.subtitle || result.type;
        
        infoDiv.appendChild(title);
        infoDiv.appendChild(subtitle);
        
        // Badge
        const badgeDiv = document.createElement('div');
        badgeDiv.className = `result-badge ${result.type}-badge`;
        
        const badgeIcon = document.createElement('i');
        const badgeText = document.createElement('span');
        
        switch(result.type) {
            case 'user':
                badgeIcon.className = 'fas fa-user-tag';
                badgeText.textContent = 'Usuario';
                break;
            case 'project':
                badgeIcon.className = 'fas fa-hammer';
                badgeText.textContent = 'Proyecto';
                break;
            case 'manager':
                badgeIcon.className = 'fas fa-crown';
                badgeText.textContent = 'Manager';
                break;
            default:
                badgeIcon.className = 'fas fa-file';
                badgeText.textContent = 'Resultado';
        }
        
        badgeDiv.appendChild(badgeIcon);
        badgeDiv.appendChild(badgeText);
        
        headerDiv.appendChild(avatarDiv);
        headerDiv.appendChild(infoDiv);
        headerDiv.appendChild(badgeDiv);
        
        return headerDiv;
    }

    //Crear detalles del resultado
    function createResultDetails(result) {
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'result-details';
        
        // Descripción
        if (result.description) {
            const description = document.createElement('p');
            description.textContent = result.description;
            detailsDiv.appendChild(description);
        }
        
        // Tags específicos según tipo
        const tags = [];
        
        if (result.type === 'user') {
            if (result.department) tags.push({icon: 'fas fa-building', text: result.department});
            if (result.position) tags.push({icon: 'fas fa-briefcase', text: result.position});
        } else if (result.type === 'project') {
            if (result.status) tags.push({icon: 'fas fa-circle', text: result.status, class: `status-${result.status}`});
            if (result.location) tags.push({icon: 'fas fa-map-marker-alt', text: result.location});
        } else if (result.type === 'manager') {
            if (result.level) tags.push({icon: 'fas fa-star', text: `Nivel ${result.level}`, class: 'level-tag'});
            if (result.points) tags.push({icon: 'fas fa-coins', text: `${result.points} pts`, class: 'points-tag'});
        }
        
        // Crear tags
        tags.forEach(tag => {
            const tagSpan = document.createElement('span');
            tagSpan.className = `detail-tag ${tag.class || ''}`;
            
            const tagIcon = document.createElement('i');
            tagIcon.className = tag.icon;
            
            const tagText = document.createTextNode(` ${tag.text}`);
            
            tagSpan.appendChild(tagIcon);
            tagSpan.appendChild(tagText);
            detailsDiv.appendChild(tagSpan);
        });
        
        return detailsDiv;
    }

    //Crear acciones del resultado
    function createResultActions(result) {
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'result-actions';
        
        const actionBtn = document.createElement('button');
        actionBtn.className = 'btn-action';
        
        const btnIcon = document.createElement('i');
        btnIcon.className = 'fas fa-eye';
        
        const btnText = document.createTextNode(' Ver');
        
        // Personalizar según tipo
        switch(result.type) {
            case 'user':
                btnText.textContent = ' Ver Perfil';
                actionBtn.onclick = () => viewUserProfile(result.id);
                break;
            case 'project':
                btnText.textContent = ' Ver Proyecto';
                actionBtn.onclick = () => viewProject(result.id);
                break;
            case 'manager':
                btnText.textContent = ' Ver Manager';
                actionBtn.onclick = () => viewManagerProfile(result.id);
                break;
            default:
                btnText.textContent = ' Ver';
                actionBtn.onclick = () => viewItem(result.id);
        }
        
        actionBtn.appendChild(btnIcon);
        actionBtn.appendChild(btnText);
        actionsDiv.appendChild(actionBtn);
        
        return actionsDiv;
    }

    //Renderizar paginación
    function renderPagination(data) {
        const paginationWrapper = document.createElement('div');
        paginationWrapper.className = 'pagination-wrapper';
        
        const paginationDiv = document.createElement('div');
        paginationDiv.className = 'pagination';
        
        // Botón anterior
        if (data.has_previous) {
            const prevBtn = createPageButton(data.current_page - 1, 'Anterior', 'fas fa-chevron-left');
            paginationDiv.appendChild(prevBtn);
        }
        
        // Números de página
        const startPage = Math.max(1, data.current_page - 2);
        const endPage = Math.min(data.total_pages, data.current_page + 2);
        
        // Primera página si es necesaria
        if (startPage > 1) {
            const firstBtn = createPageButton(1, '1');
            paginationDiv.appendChild(firstBtn);
            
            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'page-ellipsis';
                ellipsis.textContent = '...';
                paginationDiv.appendChild(ellipsis);
            }
        }
        
        // Páginas del rango
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = createPageButton(i, i.toString());
            if (i === data.current_page) {
                pageBtn.classList.add('active');
            }
            paginationDiv.appendChild(pageBtn);
        }
        
        // Última página si es necesaria
        if (endPage < data.total_pages) {
            if (endPage < data.total_pages - 1) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'page-ellipsis';
                ellipsis.textContent = '...';
                paginationDiv.appendChild(ellipsis);
            }
            
            const lastBtn = createPageButton(data.total_pages, data.total_pages.toString());
            paginationDiv.appendChild(lastBtn);
        }
        
        // Botón siguiente
        if (data.has_next) {
            const nextBtn = createPageButton(data.current_page + 1, 'Siguiente', 'fas fa-chevron-right', true);
            paginationDiv.appendChild(nextBtn);
        }
        
        paginationWrapper.appendChild(paginationDiv);
        searchPagination.appendChild(paginationWrapper);
    }

    //Crear botón de página
    function createPageButton(page, text, iconClass = null, iconRight = false) {
        const button = document.createElement('button');
        button.className = 'page-btn';
        button.onclick = () => goToPage(page);
        
        if (iconClass && !iconRight) {
            const icon = document.createElement('i');
            icon.className = iconClass;
            button.appendChild(icon);
            button.appendChild(document.createTextNode(` ${text}`));
        } else if (iconClass && iconRight) {
            button.appendChild(document.createTextNode(`${text} `));
            const icon = document.createElement('i');
            icon.className = iconClass;
            button.appendChild(icon);
        } else {
            button.textContent = text;
        }
        
        return button;
    }

    //Manejar click en resultado
    function handleResultClick(result, element) {
        // Remover selección anterior
        document.querySelectorAll('.search-result-item.selected').forEach(item => {
            item.classList.remove('selected');
        });
        
        // Agregar selección actual
        element.classList.add('selected');
        
        console.log('Result clicked:', result);
    }

    //Funciones de navegación (globales)
    window.goToPage = function(page) {
        currentPage = page;
        performSearch(currentQuery, currentPage);
    };

    window.viewUserProfile = function(userId) {
        window.location.href = `/users/${userId}/profile/`;
    };

    window.viewProject = function(projectId) {
        window.location.href = `/projects/${projectId}/`;
    };

    window.viewManagerProfile = function(managerId) {
        window.location.href = `/manager/${managerId}/profile/`;
    };

    window.viewItem = function(itemId) {
        console.log('View item:', itemId);
    };

});