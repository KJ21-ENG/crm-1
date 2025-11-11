import { createDocumentResource } from 'frappe-ui'
import { reactive, ref } from 'vue'

const settings = ref({})
const brand = reactive({})

const _settings = createDocumentResource({
  doctype: 'FCRM Settings',
  name: 'FCRM Settings',
  onSuccess: (data) => {
    settings.value = data
    getSettings().setupBrand()
    getSettings().updateFavicon()
    return data
  },
})

export function getSettings() {
  function setupBrand() {
    brand.name = settings.value?.brand_name
    brand.logo = settings.value?.brand_logo
    brand.favicon = settings.value?.favicon
  }

  function updateFavicon() {
    if (!settings.value?.favicon) return

    // Remove existing favicon links
    const existingFavicons = document.querySelectorAll('link[rel="icon"], link[rel="shortcut icon"]')
    existingFavicons.forEach(link => link.remove())

    // Add new favicon link
    const faviconLink = document.createElement('link')
    faviconLink.rel = 'icon'
    faviconLink.type = 'image/png'
    faviconLink.href = settings.value.favicon
    faviconLink.sizes = '32x32'

    document.head.appendChild(faviconLink)
  }

  return {
    _settings,
    settings,
    brand,
    setupBrand,
    updateFavicon,
  }
}
