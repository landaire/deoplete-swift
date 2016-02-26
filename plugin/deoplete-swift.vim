if exists('g:loaded_deoplete_swift')
  finish
endif
let g:loaded_deoplete_d = 1

if !exists("g:deoplete#sources#swift#source_kitten_binary")
  let g:deoplete#sources#swift#source_kitten_binary = ''
endif

