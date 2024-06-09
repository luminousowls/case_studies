document.addEventListener('DOMContentLoaded', (event) => {

    let sidebar = document.getElementById('sidebar');
    let toggleSidebarButton = document.getElementById('toggle-sidebar-button');
    let contentWrapper = document.querySelector('.content-wrapper');

    function toggleSidebar() {
        sidebar.classList.toggle('show-sidebar');
        if (sidebar.classList.contains('show-sidebar')) {
            contentWrapper.classList.add('sidebar-visible');
        } else {
            contentWrapper.classList.remove('sidebar-visible');
        }
    }

    toggleSidebarButton.addEventListener('click', toggleSidebar);
});