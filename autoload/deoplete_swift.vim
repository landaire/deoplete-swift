let s:placeholder_pattern = '<#\%(T##\)\?\%([^#]\+##\)\?\([^#]\+\)#>'

function! deoplete_swift#jump_to_placeholder()
    if &filetype !=# 'swift'
        return ''
    end

    if !deoplete_swift#check_placeholder_existence()
        return ''
    endif

    return "\<ESC>:call deoplete_swift#begin_replacing_placeholder()\<CR>"
endfunction

function! deoplete_swift#check_placeholder_existence()
    return search(s:placeholder_pattern)
endfunction

function! deoplete_swift#begin_replacing_placeholder()
    if mode() !=# 'n'
        return
    endif

    let [l:line, l:column] = searchpos(s:placeholder_pattern)
    if l:line == 0 && l:column == 0
        return
    end

    execute printf(':%d s/%s//', l:line, s:placeholder_pattern)

    call cursor(l:line, l:column)

    startinsert
endfunction
