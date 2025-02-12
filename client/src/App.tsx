import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import MyParticles from './components/Particles';

const App: React.FC = () => {
    const [preview, setPreview] = useState('');
    const [result, setResult] = useState('');
    const [type, setType] = useState('');
    const [confidence, setConfidence] = useState('');

    const onDrop = useCallback(async (acceptedFiles: any[]) => {
        try {
            const file = acceptedFiles[0];
            setPreview(URL.createObjectURL(file));
            const formData = new FormData();
            formData.append('image', file);
            const res = await axios.post(
                'http://127.0.0.1:5000/colorize',
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    },
                    responseType: 'blob'
                }
            );

            const formData2 = new FormData();
            formData2.append('image', res.data);
            const res2 = await axios.post(
                'http://127.0.0.1:5000/classify',
                formData2,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                }
            );
            setType(res2.data.class);
            setConfidence(res2.data.confidence);
            setResult(URL.createObjectURL(res.data));
        } catch (error) {
            alert('Something went wrong');
            console.error(error);
        }
    }, []);
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop
    });

    return (
        <div className="flex min-h-screen flex-col justify-center items-center">
            <MyParticles />
            <div className="flex flex-col justify-center items-center shadow-2xl p-10 z-50 bg-black text-white">
                <h1 className="text-4xl font-bold mb-5">
                    📡 SAR Image Enhancement and Terrain Classification Methods
                </h1>
                <main className="flex gap-2.5 mb-5">
                    {!preview ? (
                        <div
                            {...getRootProps()}
                            className="border border-dashed p-10"
                        >
                            <input {...getInputProps()} />
                            {isDragActive ? (
                                <p>Drop the files here ...</p>
                            ) : (
                                <p>
                                    Drag 'n' drop some files here, or click to
                                    select files
                                </p>
                            )}
                        </div>
                    ) : (
                        <div>
                            <img
                                src={preview}
                                className="object-contain"
                                alt="Preview Image"
                                height={256}
                                width={256}
                            />
                        </div>
                    )}
                    {result && (
                        <img
                            src={result}
                            className="object-contain"
                            alt="Result Image"
                            height={256}
                            width={256}
                        />
                    )}
                </main>
                {type && (
                    <p className="text-lg">
                        Type: <span className="font-semibold">{type}</span>
                    </p>
                )}
                {confidence && (
                    <p className="text-lg">
                        {' '}
                        Confidence:{' '}
                        <span className="font-semibold">
                            {(parseFloat(confidence) * 100).toFixed(2)} %
                        </span>
                    </p>
                )}
                {result && (
                    <button
                        className="bg-teal-400 text-white rounded-full px-8 py-2 mt-5 font-semibold cursor-pointer"
                        onClick={() => {
                            setPreview('');
                            setResult('');
                            setType('');
                            setConfidence('');
                        }}
                    >
                        Upload Again
                    </button>
                )}
            </div>
        </div>
    );
};

export default App;
