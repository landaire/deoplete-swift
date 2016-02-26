# deoplete-swift

Adds auto-complete support for the Swift programming language to Vim

## Installation

Using your favorite package manager or whatever (idk, you probably know vim
better than I do):

```
Plug 'landaire/deoplete-swift'
```

## Configuration

Default configuration:

`let g:deoplete#sources#swift#sourcekittendaemon = ''` location of the `sourcekittendaemon`
on your system. This is optional and will be found in your `$PATH` if not set

`let g:deoplete#sources#swift#daemon_autostart = 1` - whether or not `sourcekittendaemon`
should be auto-started

