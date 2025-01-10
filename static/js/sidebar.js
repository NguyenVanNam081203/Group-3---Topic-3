document.getElementById('toggleSidebar').addEventListener('click', function () {
    const sidebar = document.querySelector('.sidebar');
    const header = document.querySelector('.header');
    const searchSection = document.querySelector('.search-section');
    const results = document.querySelector('.results');
  
    sidebar.classList.toggle('collapsed');
    header.classList.toggle('collapsed');
    searchSection.classList.toggle('collapsed');
    results.classList.toggle('collapsed');
  });
  