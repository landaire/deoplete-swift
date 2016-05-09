# deoplete-swift

Adds auto-complete support for the Swift programming language to Vim

## Installation

Using your favorite package manager or whatever (idk, you probably know vim
better than I do):

```
Plug 'landaire/deoplete-swift'
```

For jumping to placeholders, add the following keymapping to your configuration:

```vim
" Jump to the first placeholder by typing `<C-j>`.
autocmd FileType swift imap <buffer> <C-j> <Plug>(deoplete_swift_jump_to_placeholder)
```

## Configuration

Default configuration:

`let g:deoplete#sources#swift#source_kitten_binary = ''` location of `sourcekitten`
on your system. This is optional and will be found in your `$PATH` if not set

# TODO:

- [ ] Add sourcekittendaemon support (#2). This will allow better project-based completion
