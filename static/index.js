$(document).ready(function () {
    //get_definitions();
    get_examples();
});
function get_definitions() {
    let api_key = '25e04055-eb58-4447-906c-d32c3200310f';
    let url = `https://www.dictionaryapi.com/api/v3/references/collegiate/json/${word}?key=${api_key}`;
    $.ajax({
        type: 'GET',
        url: url,
        data: {},
        success: function (response) {
            let def = response[0];
            let category = def.fl;
            let shortdef = def.shortdef[0];
            let date = def.date;
            let temp_html = `
                            <div style="padding: 10px">
                            <i>${category}</i>
                            <br />
                            ${shortdef}
                            <br />
                            <span class="example">${date}</span>
                            </div>
                                    `;
            let container = $('#definition');
            container.empty();
            container.append(temp_html);
        }
    });
}

// Jika kata yang kita cari sudah ada di list kata-kata kita, kita harus memberinya highlight dan menscroll ke kata tersebut dalam list kita 
// Tetapi, jika kata tersebut belum ada di list kata yang sudah tersimpan, kita harus pergi langsung ke laman detail untuk kata tersebut.
function find_word() {
    let word = $('#input-word').val().toLowerCase().trim();
    // ini jika kita tidak memasukkan kata
    if (!word) {
        alert('Please type a word');
        return;
    }
    // jika kata/wordnya sama maka akan terhighligth
    if (word_list.includes(word)) {
        let row = $(`#word-${word}`);
        row.addClass('highlight');
        row.siblings().removeClass('highlight');
        row[0].scrollIntoView();
    // jika tidak ada word yang sama maka akan memunculkan ini 
    } else {
        window.location.href = `/detail/${word}?status_give=new`;
    }
}