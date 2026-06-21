import {useState} from "react";
import api from "../api/client";


function Upload(){

const [file,setFile]=useState(null);


async function upload(){

const formData=new FormData();

formData.append(
"file",
file
);


await api.post(
"/api/v1/documents/upload",
formData
);

alert("Uploaded");

}


return (

<div>

<h1>
Upload Document
</h1>


<input

type="file"

accept=".pdf"

onChange={
(e)=>setFile(e.target.files[0])
}

/>


<button onClick={upload}>
Upload
</button>


</div>

)

}


export default Upload;