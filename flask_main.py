from flask import Flask, request
import datetime
import logging, traceback
from order_management import handle_alert

file_handler = logging.FileHandler('log.log')
logging.basicConfig(handlers=[file_handler], level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

app = Flask('__name__')

def error_handler(func, *args, **kwargs):
    # wrapper function for handling errors
    try:
        return func(*args, **kwargs)
    except Exception as e:
        #assign exception to the error_type
        print(f'ERROR IN {func} @ {datetime.datetime.now().time().replace(microsecond=0)} : {e}')
        logging.error(f'ERROR IN {func} @ {datetime.datetime.now().time().replace(microsecond=0)} : {e}')
        logging.error(f'FUNCTION ARGUMENTS ARE :{args}, {kwargs}')
        logging.error(traceback.format_exc())
        return


@app.route('/', methods=['POST'])
def tv():
    try:
        message = request.data.decode('utf-8')
        if 'intention' in message:
            exit_alert = {}
            for a in message.split(','):
                key = a.split(':')[0].replace('"',"").strip()
                val = a.split(':')[1].replace('"',"").strip()
                exit_alert[key]=val
            exit_alert['message'] = message
            logging.warning(exit_alert)
            return 'Exit Alert Executed'

        elif 'Side' in message :
            
            entry_alert = {}
            for a in message.split(','):
                key = a.split(':')[0].replace('"',"").strip()
                val = a.split(':')[1].replace('"',"").strip()
                entry_alert[key]=val
            print(entry_alert)
            logging.warning(entry_alert)
            order_details = error_handler(handle_alert, entry_alert)

            return 'Entry Alert Executed'

        else:
            print(message)
            logging.error(message)
            return 'The message is unusual. Please check the log file'
        
    except Exception as e:
        print(f'While parsing webhook message: {message} Error occured : {e}')
        logger.error(traceback.format_exc())
        return 'There is some problem in flask servers'

if __name__ == '__main__':
    app.run(debug=True)