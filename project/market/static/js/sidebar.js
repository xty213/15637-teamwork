$('#left-col').affix({
  offset: {
    top: 0,
    bottom: function () {
      return (this.bottom = $('#footer-wrapper').outerHeight(true))
    }
  }
})