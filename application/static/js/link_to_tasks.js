// Эта функция динамечески изменяет ссылку на файл с заданием

function changeLink(){
	var RUS_TO_ENG = {
        "Астрономия": "Astronomy",
        "География": "Geography",
        "Испанский язык": "Spanish",
        "История": "History",
        "Китайский язык": "Chinese",
        "МХК": "MHK",
        "Немецкий язык": "German",
        "Обществознание": "Social",
        "ОБЖ": "OBJ",
        "Физкультура": "PE",
        "Философия": "Philosophy",
        "Французский язык": "French",
        "Экология": "Ecology",
        "Экономика": "Economy",
        "Математика": "Math",
        "Русский язык": "Russian",
        "Информатика": "Informatics",
        "Физика": "Physics",
        "Литература": "Literature",
        "Английский язык": "English",
        "Химия": "Chemistry",
        "Биология": "Biology"
    }

	var subject = RUS_TO_ENG[document.getElementById("subject").value];
	var grade = document.getElementById("grade").value;
	var olimp_id = document.getElementById("olimpiad_id").textContent;

	var link = document.getElementById("load_file");
	link.href = "../static/tasks/" + olimp_id + "_" + subject + "_" + grade + ".zip";
}

