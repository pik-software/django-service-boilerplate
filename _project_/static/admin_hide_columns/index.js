((global) => {
	let $
	let key = `${window.location.pathname}_hiddenColumns`
	const SORTABLE = 'sortable'
	const CHECKBOX = 'action-checkbox'
	const HIDEBUTTON = 'hideButton'
	const RESTORECOLUMNS = 'restoreColumns'
	const HEADERBUTTON = 'headerButton'

	document.addEventListener('DOMContentLoaded', () => {
		if (!(global.django && django.jQuery)) return
		$ = django.jQuery
  		let cols = $('th[scope="col"]')
		let hiddenColumns = loadHiddenColumns()
  		if (cols.length) appendHeader()
		cols.each((i, col) => {
			if(col.className.indexOf(CHECKBOX) === -1) {
				let columnName = `.${col.className.replace(SORTABLE,'').trim()}`
				let title = col.innerText
				prepareColumn(columnName, title)
				setState(hiddenColumns, columnName)
			}
		})

	})

	function prepareColumn (columnName, title) {
		let hideButton = $(`<div class='${HIDEBUTTON}'>✖</div>`)
			.on('click', () => {
				$Column(columnName).hide()
			})

		let headerButton = $(`<div class='${HEADERBUTTON} ${columnName.substr(1)}'>${title}</div>`)
			.on('click', () => {
				$Column(columnName).show()
			})

		$(columnName).prepend(hideButton)
		$(`.${RESTORECOLUMNS}`).append(headerButton)
	}

	function setState (hiddenColumns, columnName) {
		if(hiddenColumns[columnName]) {
			$Column(columnName).hide()
		}
	}

	function appendHeader () {
		let restoreColumns = `<div class="${RESTORECOLUMNS}">&nbsp;</div>`
		$('table').prepend(restoreColumns)
	}

	function $Column (columnName) {
		let fieldsName = columnName.replace('column', 'field')
		let column = $([columnName, fieldsName].join(','))
		let button = $HeaderButton(columnName)
		return {
			show () {
				column.show()
				button.hide()
				saveHiddenColumn(columnName, false)
			},
			hide () {
				column.hide()
				button.show()
				saveHiddenColumn(columnName, true)
			}
		}
	}

	function $HeaderButton (columnName) {
		return $(`.${HEADERBUTTON}${columnName}`)
	}

	function loadHiddenColumns () {
		let value = localStorage.getItem(key)
		return JSON.parse(value) || {}
	}

	function saveHiddenColumn (column, state) {
		let hiddenColumns = loadHiddenColumns()
		hiddenColumns[column] = state

		let value = JSON.stringify(hiddenColumns)
		localStorage.setItem(key, value)
	}

})(window)
